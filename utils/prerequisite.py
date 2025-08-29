import logging

import torch
from nlu_processor import NLUProcessor
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
SAMPLE_RATE = 0


async def initial(logger):
    global \
        MODEL_LOADED, \
        PIPE, \
        DEVICE, \
        NLU_PROCESSOR, \
        VAD_MODEL, \
        GET_SPEECH_TIMESTAMPS, \
        COLLECT_CHUNKS
    try:
        # Load Whisper model
        logger.info("Loading speech recognition model...")
        DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {DEVICE}")

        print("Before loading the model")
        # local_dir = "../whisper_models/whisper-large-v3/models--openai--whisper-large-v3/snapshots/91d5775ea8268a1f9edfcf16afcc4f68802940d0"
        MODEL_ID = "openai/whisper-large-v3-turbo"
        local_dir = "./whisper_models/whisper-large-v3-turbo"

        torch_dtype = (
            torch.float16
            if torch.cuda.is_available() and torch.cuda.get_device_capability(0)[0] >= 8
            else torch.float32
        )

        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            MODEL_ID,
            cache_dir=local_dir,  # download if not cached
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True,
        )

        processor = AutoProcessor.from_pretrained(MODEL_ID, cache_dir=local_dir)

        PIPE = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            max_new_tokens=256,
            chunk_length_s=30,
            batch_size=1,
            torch_dtype=torch_dtype,
            device=0 if torch.cuda.is_available() else -1,
        )
        MODEL_LOADED = True
        logger.info("Whisper model loaded and pipeline ready.")

        # Load Silero VAD
        logger.info("Loading Silero VAD...")
        vad_bundle = torch.hub.load(
            repo_or_dir="snakers4/silero-vad", model="silero_vad"
        )
        VAD_MODEL, vad_utils = vad_bundle
        (GET_SPEECH_TIMESTAMPS, _, _, _, COLLECT_CHUNKS) = vad_utils
        logger.info("Silero VAD loaded.")

        # Load Rasa model
        logger.info("Loading Rasa NLU model...")
        NLU_MODEL_PATH = "models/nlu_two_intent_classifier.tar.gz"
        NLU_PROCESSOR = NLUProcessor.create(NLU_MODEL_PATH)
        if NLU_PROCESSOR:
            logger.info("✅ Rasa NLUProcessor initialized successfully.")
        else:
            logger.error("Failed to initialize Rasa NLUProcessor.")

        yield

    except Exception as e:
        logger.exception("Failed to load models:", e)
        MODEL_LOADED = False
        NLU_PROCESSOR = None
        yield
    finally:
        logger.info("Shutting down...")


