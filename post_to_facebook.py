import os
from pathlib import Path

import requests


def load_local_env_if_present():
    # Only load .env in local development
    if os.path.exists(".env"):
        from dotenv import load_dotenv
        load_dotenv()


def get_facebook_credentials():
    load_local_env_if_present()

    page_id = os.getenv("FB_PAGE_ID")
    access_token = os.getenv("FB_PAGE_ACCESS_TOKEN")

    if not page_id:
        raise RuntimeError(
            "Error: Missing environment variable 'FB_PAGE_ID'. Ensure it's set in the environment."
        )

    if not access_token:
        raise RuntimeError(
            "Error: Missing environment variable 'FB_PAGE_ACCESS_TOKEN'. Ensure it's set in the environment."
        )

    return page_id, access_token


def upload_image_unpublished(image_path, page_id, access_token):
    """
    Upload image to Facebook without publishing.
    Returns media_fbid.
    """
    url = f"https://graph.facebook.com/v19.0/{page_id}/photos"

    with open(image_path, "rb") as image_file:
        files = {"source": image_file}
        data = {
            "published": "false",
            "access_token": access_token,
        }

        response = requests.post(url, files=files, data=data)

    if response.status_code != 200:
        raise RuntimeError(
            f"Image upload failed ({response.status_code}): {response.text}"
        )

    return response.json()["id"]


def post_multiple_images_single_post(
    charts_dir,
    caption="📊 Market Charts Summary",
):
    page_id, access_token = get_facebook_credentials()

    image_paths = sorted(Path(charts_dir).glob("*.png"))

    if not image_paths:
        print("No images found to post.")
        return

    print(f"Uploading {len(image_paths)} images...")

    media_fbids = []
    for image_path in image_paths:
        print(f"Uploading {image_path.name}")
        media_id = upload_image_unpublished(
            image_path=str(image_path),
            page_id=page_id,
            access_token=access_token,
        )
        media_fbids.append({"media_fbid": media_id})

    print("Creating single Facebook post...")

    post_url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
    data = {
        "message": caption,
        "attached_media": media_fbids,
        "access_token": access_token,
    }

    response = requests.post(post_url, json=data)

    if response.status_code != 200:
        raise RuntimeError(
            f"Post creation failed ({response.status_code}): {response.text}"
        )

    print("✅ Single multi-image post created successfully!")
    return response.json()


if __name__ == "__main__":
    # Example direct-run usage
    post_multiple_images_single_post("charts")