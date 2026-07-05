from fastapi import Request
from app.services.retrieval import RetrievalService
from app.services.generation import GenerationService


def get_retriever(request: Request) -> RetrievalService:
    return request.app.state.retriever


def get_generator(request: Request) -> GenerationService:
    return request.app.state.generator
