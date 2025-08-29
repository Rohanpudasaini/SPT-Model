import asyncio
import logging
from concurrent import futures
from typing import List

import grpc
import numpy as np
import speech_service_pb2 as speech_pb2
from speech_service_pb2_grpc import (
    SpeechServiceServicer,
    add_SpeechServiceServicer_to_server,
)

# Import the dynamically generated classes
TranscribeAudioRequest = speech_pb2.TranscribeAudioRequest
TranscribeAudioResponse = speech_pb2.TranscribeAudioResponse
MergeTranscriptionsRequest = speech_pb2.MergeTranscriptionsRequest
MergeTranscriptionsResponse = speech_pb2.MergeTranscriptionsResponse
ProcessIntentRequest = speech_pb2.ProcessIntentRequest
ProcessIntentResponse = speech_pb2.ProcessIntentResponse
Entity = speech_pb2.Entity
HealthCheckRequest = speech_pb2.HealthCheckRequest
HealthCheckResponse = speech_pb2.HealthCheckResponse

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global variables for model state
NLU_PROCESSOR = None


class SpeechServiceImpl(SpeechServiceServicer):
    """Implementation of the SpeechService gRPC service."""

    async def TranscribeAudioSegment(self, request, context):
        """Transcribe an audio segment."""
        try:
            if not MODEL_LOADED:
                return speech_pb2.TranscribeAudioResponse(
                    transcription="", success=False, error_message="Model not loaded"
                )

            # Convert base64 audio data to numpy array
            audio_bytes = request.audio_data
            audio_np = np.frombuffer(audio_bytes, dtype=np.float32)

            # Transcribe the audio
            transcription = await transcribe_segment(audio_np, request.language)

            return speech_pb2.TranscribeAudioResponse(
                transcription=transcription, success=True, error_message=""
            )

        except Exception as e:
            logger.exception(f"Error transcribing audio: {e}")
            return speech_pb2.TranscribeAudioResponse(
                transcription="", success=False, error_message=str(e)
            )

    async def MergeTranscriptions(self, request, context):
        """Merge multiple transcriptions into a single text."""
        try:
            transcriptions = [t for t in request.transcriptions if t.strip()]

            if not transcriptions:
                return speech_pb2.MergeTranscriptionsResponse(
                    merged_text="", success=True, error_message=""
                )

            # Simple merging strategy - join with spaces and clean up
            merged_text = " ".join(transcriptions)

            # Remove excessive whitespace
            merged_text = " ".join(merged_text.split())

            return speech_pb2.MergeTranscriptionsResponse(
                merged_text=merged_text, success=True, error_message=""
            )

        except Exception as e:
            logger.exception(f"Error merging transcriptions: {e}")
            return speech_pb2.MergeTranscriptionsResponse(
                merged_text="", success=False, error_message=str(e)
            )

    async def ProcessIntent(self, request, context):
        """Process text for intent analysis and entity extraction."""
        try:
            global NLU_PROCESSOR

            if not NLU_PROCESSOR:
                return speech_pb2.ProcessIntentResponse(
                    action="error",
                    message="NLU processor not initialized",
                    form_data={},
                    entities=[],
                    confidence=0.0,
                    success=False,
                    error_message="NLU processor not available",
                )

            # Process the intent
            result = await NLU_PROCESSOR.process_command(
                request.text, confidence_threshold=request.confidence_threshold or 0.80
            )

            # Convert entities to proto format
            entities = []
            if "entities" in result and result["entities"]:
                for entity in result["entities"]:
                    entities.append(
                        speech_pb2.Entity(
                            entity=entity.get("entity", ""),
                            value=entity.get("value", ""),
                            confidence=entity.get("confidence", 0.0),
                            start=entity.get("start", 0),
                            end=entity.get("end", 0),
                        )
                    )

            return speech_pb2.ProcessIntentResponse(
                action=result.get("action", "unknown"),
                message=result.get("message", ""),
                form_data=result.get("form_data", {}),
                entities=entities,
                confidence=result.get("confidence", 0.0),
                success=True,
                error_message="",
            )

        except Exception as e:
            logger.exception(f"Error processing intent: {e}")
            return speech_pb2.ProcessIntentResponse(
                action="error",
                message="Intent processing failed",
                form_data={},
                entities=[],
                confidence=0.0,
                success=False,
                error_message=str(e),
            )

    async def HealthCheck(self, request, context):
        """Health check for the model service."""
        try:
            loaded_models = []
            if MODEL_LOADED:
                loaded_models.append("whisper")
            if PIPE is not None:
                loaded_models.append("speech_recognition")
            if VAD_MODEL is not None:
                loaded_models.append("vad")
            if NLU_PROCESSOR is not None:
                loaded_models.append("rasa_nlu")

            return speech_pb2.HealthCheckResponse(
                healthy=MODEL_LOADED,
                status="healthy" if MODEL_LOADED else "unhealthy",
                version="1.0.0",
                loaded_models=loaded_models,
            )

        except Exception as e:
            logger.exception(f"Error in health check: {e}")
            return speech_pb2.HealthCheckResponse(
                healthy=False, status="error", version="1.0.0", loaded_models=[]
            )


async def serve():
    """Start the gRPC server."""
    # Initialize models
    logger.info("Initializing models...")
    async for _ in initial(logger):
        pass

    global NLU_PROCESSOR
    # Load NLU processor
    try:
        NLU_PROCESSOR = NLUProcessor.create("models/nlu_two_intent_classifier.tar.gz")
        if NLU_PROCESSOR:
            logger.info("✅ Rasa NLUProcessor initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize NLU processor: {e}")
        NLU_PROCESSOR = None

    # Create gRPC server
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    add_SpeechServiceServicer_to_server(SpeechServiceImpl(), server)
    server.add_insecure_port("[::]:50051")

    logger.info("Starting gRPC server on port 50051...")
    await server.start()
    logger.info("Server started successfully!")

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        await server.stop(0)


if __name__ == "__main__":
    asyncio.run(serve())
