from fastapi import APIRouter

from app.services import defaults as defaults_service

router = APIRouter()


@router.get("/languages")
def get_languages():
    return defaults_service.get_languages()


@router.get("/voices")
def get_voices():
    return defaults_service.get_voices()


@router.get("/transcriptions-models")
def get_transcriptions_models():
    return defaults_service.get_transcriptions_models()
