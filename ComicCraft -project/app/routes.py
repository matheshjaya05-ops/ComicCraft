@router.get("/test-image")
async def test_image(
    prompt: str = "A cute fox hero in an enchanted forest, comic book art"
):
    try:
        from .config import HF_TOKEN, USE_MOCK_AI

        image_path = generate_image(
            prompt,
            1
        )

        return {
            "success": True,
            "image_path": image_path,
            "hf_token_configured": bool(HF_TOKEN),
            "use_mock_ai": USE_MOCK_AI
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )   