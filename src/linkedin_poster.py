"""
Posts to LinkedIn via the UGC Posts API (v2).

Supports:
- Text-only posts
- Article link preview posts
- Image posts (upload image + text)
"""

from typing import Optional

import requests

from config.settings import settings


class LinkedInPoster:
    LINKEDIN_API_BASE = "https://api.linkedin.com/v2"

    def __init__(self):
        self.access_token = settings.linkedin_access_token
        self.person_urn = settings.linkedin_person_urn
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        })

    def create_text_post(self, text: str) -> Optional[str]:
        """Create a simple text-only post. Returns the post URN on success."""
        payload = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }
        return self._post(payload)

    def create_article_post(
        self, text: str, article_url: str, article_title: str = ""
    ) -> Optional[str]:
        """Create a post with an article link preview. Returns the post URN on success."""
        media_item = {
            "status": "READY",
            "originalUrl": article_url,
        }
        if article_title:
            media_item["title"] = {"text": article_title}

        payload = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "ARTICLE",
                    "media": [media_item],
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }
        return self._post(payload)

    def create_image_post(self, text: str, image_data: bytes) -> Optional[str]:
        """
        Create a post with an uploaded image.
        Steps: 1) Register upload 2) Upload binary 3) Create post with asset
        """
        # Step 1: Register the upload
        register_payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": self.person_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent",
                    }
                ],
            }
        }

        try:
            reg_resp = self.session.post(
                f"{self.LINKEDIN_API_BASE}/assets?action=registerUpload",
                json=register_payload,
                timeout=15,
            )
            reg_resp.raise_for_status()
            reg_data = reg_resp.json()

            upload_url = reg_data["value"]["uploadMechanism"][
                "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
            ]["uploadUrl"]
            asset = reg_data["value"]["asset"]
            print(f"[LinkedInPoster] Registered upload: {asset}")

        except (requests.RequestException, KeyError) as e:
            print(f"[LinkedInPoster] Upload registration failed: {e}")
            return None

        # Step 2: Upload the image binary
        try:
            upload_resp = requests.put(
                upload_url,
                data=image_data,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/octet-stream",
                },
                timeout=30,
            )
            upload_resp.raise_for_status()
            print(f"[LinkedInPoster] Image uploaded successfully")

        except requests.RequestException as e:
            print(f"[LinkedInPoster] Image upload failed: {e}")
            return None

        # Step 3: Create the post with the uploaded image
        payload = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "media": asset,
                        }
                    ],
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }
        return self._post(payload)

    def _post(self, payload: dict) -> Optional[str]:
        """Send the post request to LinkedIn API."""
        try:
            resp = self.session.post(
                f"{self.LINKEDIN_API_BASE}/ugcPosts",
                json=payload,
                timeout=15,
            )
            resp.raise_for_status()
            post_urn = resp.headers.get("X-RestLi-Id")
            print(f"[LinkedInPoster] Post created: {post_urn}")
            return post_urn
        except requests.RequestException as e:
            print(f"[LinkedInPoster] Posting failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"  Response: {e.response.text}")
            return None
