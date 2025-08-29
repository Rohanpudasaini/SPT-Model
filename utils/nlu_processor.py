import logging
from typing import Any, Dict, Optional

import numpy as np
import torch


from rasa.core.agent import Agent
from utils.utils import prerequisite

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
MODEL_LOADED = True





async def transcribe_segment(audio_np_segment: np.ndarray, language: str) -> str:
    GET_SPEECH_TIMESTAMPS = prerequisite['GET_SPEECH_TIMESTAMPS']
    VAD_MODEL = prerequisite['VAD_MODEL']
    SAMPLE_RATE = prerequisite['SAMPLE_RATE']
    COLLECT_CHUNKS = prerequisite['COLLECT_CHUNKS']
    PIPE = prerequisite['PIPE']
    if not MODEL_LOADED:
        logger.error("Transcription requested but model not loaded.")
        raise RuntimeError("Model not loaded.")
    try:
        # Apply VAD to filter silence
        audio_torch = torch.from_numpy(audio_np_segment).float()
        speech_timestamps = GET_SPEECH_TIMESTAMPS(
            audio_torch,
            VAD_MODEL,
            sampling_rate=SAMPLE_RATE,
            threshold=0.3,  # Lowered threshold for more sensitivity
            min_speech_duration_ms=100,
            min_silence_duration_ms=100,
            return_seconds=False,
        )
        if not speech_timestamps:
            return ""
        filtered_audio_torch = COLLECT_CHUNKS(speech_timestamps, audio_torch)
        filtered_audio_np = filtered_audio_torch.numpy()

        # Transcription with improved parameters (removed initial_prompt as it's not supported)
        generate_kwargs = {
            "language": language,
            "temperature": 0.0,
            "num_beams": 5,
        }
        result = PIPE(filtered_audio_np, generate_kwargs=generate_kwargs)
        return result["text"].strip()  # type: ignore
    except Exception:
        logger.exception("Transcription error:")
        return ""


class NLUProcessor:
    """
    A class to load a Rasa model and use it for NLU-only tasks.
    """

    def __init__(self, agent: Agent):
        self.agent = agent
        if self.agent:
            logger.info("✅ Rasa NLUProcessor initialized successfully.")

    @classmethod
    def create(cls, model_path: str) -> Optional["NLUProcessor"]:
        """
        Loads the Rasa model and returns a class instance.

        Args:
            model_path: Path to the trained Rasa model (.tar.gz).

        Returns:
            An instance of NLUProcessor, or None if loading fails.
        """
        try:
            agent = Agent.load(model_path=model_path)
            return cls(agent)
        except Exception as e:
            logger.error(f"❌ Error loading Rasa model: {e}")
            return None

    async def classify_intent(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Uses the loaded agent to classify the intent of the given text.

        Args:
            text: The user input text.

        Returns:
            The classification result dictionary from Rasa, or None.
        """
        if not self.agent:
            logger.error("Agent not available. Cannot classify intent.")
            return None

        result = await self.agent.parse_message(text)
        return result or None

    async def process_command(self, text: str, confidence_threshold: float = 0.80):
        """
        Processes a text command, classifies it, and prepares form data.

        Args:
            text: The user input text.
            confidence_threshold: The minimum confidence to consider an intent valid.

        Returns:
            Dictionary with action, message, and form data (if applicable).
        """
        classification_result = await self.classify_intent(text)

        if classification_result:
            intent = classification_result.get("intent", {})
            intent_name = intent.get("name")
            confidence = intent.get("confidence")

            logger.info(
                f"--- Rasa NLU Analysis --- Intent: {intent_name}, Confidence: {confidence:.2f}"
            )

            # Extract entities for form filling
            entities = classification_result.get("entities", [])
            form_data = {}
            for entity in entities:
                if entity["entity"] == "amount":
                    form_data["amount"] = entity["value"]
                elif entity["entity"] == "person":
                    form_data["name"] = entity["value"]

            if confidence and confidence > confidence_threshold:
                if intent_name == "top_up":
                    logger.info("Action: Initiating 'mobile top-up' flow...")
                    return {
                        "action": "top_up",
                        "message": "Initiating 'mobile top-up' flow...",
                        "form_data": form_data,
                    }
                elif intent_name == "topup_wallet":
                    logger.info("Action: Initiating 'wallet top-up' flow...")
                    return {
                        "action": "topup_wallet",
                        "message": "Initiating 'wallet top-up' flow...",
                        "form_data": form_data,
                    }
                elif intent_name == "send_money":
                    logger.info("Action: Initiating 'send money' flow...")
                    return {
                        "action": "send_money",
                        "message": "Initiating 'send money' flow...",
                        "form_data": form_data,
                        "entities": entities,
                    }
                elif intent_name == "multicurrency_wallet":
                    logger.info("Action: Initiating 'multicurrency wallet' flow...")
                    return {
                        "action": "multicurrency_wallet",
                        "message": "Initiating 'multicurrency wallet' flow...",
                        "form_data": form_data,
                        "entities": entities,
                    }
                elif intent_name == "card_to_card_transfer":
                    logger.info("Action: Initiating 'card to card transfer' flow...")
                    return {
                        "action": "card_to_card_transfer",
                        "message": "Initiating 'card to card transfer' flow...",
                        "form_data": form_data,
                    }
                else:
                    logger.info(
                        f"Action: Intent recognized, but no specific action defined: {intent_name}"
                    )
                    return {
                        "action": "unknown",
                        "message": "Intent recognized, but no specific action defined.",
                        "form_data": form_data,
                    }
            else:
                logger.info(
                    f"Action: Confidence ({confidence:.2f}) below threshold ({confidence_threshold})."
                )
                return {
                    "action": "unknown",
                    "message": "Could not determine action. Confidence is below threshold.",
                    "form_data": form_data,
                }
        else:
            logger.error("No classification result received.")
            return {
                "action": "unknown",
                "message": "No classification result received.",
                "form_data": {},
            }
