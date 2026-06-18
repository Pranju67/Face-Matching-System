"""
FaceMatch Pro - Face Matching Engine
Uses OpenCV + NumPy for face detection and similarity computation.
No heavy AI frameworks required.
"""

import time
import os
from typing import Dict, Any, Optional, Tuple
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from skimage.metrics import structural_similarity as ssim
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False


# ─── Haar cascade path helper ──────────────────────────────────────────────────

def _get_cascade_path() -> Optional[str]:
    if not CV2_AVAILABLE:
        return None
    base = cv2.data.haarcascades
    path = os.path.join(base, "haarcascade_frontalface_default.xml")
    return path if os.path.exists(path) else None


# ─── Core matching class ────────────────────────────────────────────────────────

class FaceMatcher:
    """
    Multi-method face similarity scorer.

    Pipeline:
      1. Load & validate images
      2. Detect & crop face region
      3. Normalize to fixed size
      4. Compute histogram similarity
      5. Compute structural similarity (SSIM)
      6. Compute feature vector cosine similarity
      7. Weighted blend → final 0–100 score
    """

    FACE_SIZE = (128, 128)
    WEIGHTS = {
        "histogram": 0.30,
        "ssim": 0.35,
        "feature": 0.35,
    }
    MATCH_THRESHOLD = 60.0   # default; overridden by settings

    def __init__(self, threshold: float = 60.0):
        self.threshold = threshold
        self.cascade_path = _get_cascade_path()
        self._face_cascade = None
        if self.cascade_path:
            try:
                self._face_cascade = cv2.CascadeClassifier(self.cascade_path)
            except Exception:
                self._face_cascade = None

    # ── public entry point ──────────────────────────────────────────────────────

    def compare(self, path1: str, path2: str) -> Dict[str, Any]:
        """
        Compare two image files.
        Returns a result dict with score, status, and diagnostics.
        """
        t0 = time.perf_counter()

        result: Dict[str, Any] = {
            "similarity_score": 0.0,
            "match_status": "No Match",
            "match_label": "No Match",
            "confidence": 0.0,
            "face_quality_1": 0.0,
            "face_quality_2": 0.0,
            "dims_1": (0, 0),
            "dims_2": (0, 0),
            "processing_time": 0.0,
            "error": None,
            "histogram_score": 0.0,
            "ssim_score": 0.0,
            "feature_score": 0.0,
        }

        if not CV2_AVAILABLE:
            result["error"] = "OpenCV not installed. Run: pip install opencv-python"
            return result

        # Load images
        img1 = self._load_image(path1)
        img2 = self._load_image(path2)

        if img1 is None:
            result["error"] = f"Cannot load image: {os.path.basename(path1)}"
            return result
        if img2 is None:
            result["error"] = f"Cannot load image: {os.path.basename(path2)}"
            return result

        result["dims_1"] = (img1.shape[1], img1.shape[0])
        result["dims_2"] = (img2.shape[1], img2.shape[0])

        # Detect & crop faces
        face1, q1, err1 = self._extract_face(img1)
        face2, q2, err2 = self._extract_face(img2)

        if err1:
            result["error"] = f"Image 1: {err1}"
            return result
        if err2:
            result["error"] = f"Image 2: {err2}"
            return result

        result["face_quality_1"] = round(q1, 2)
        result["face_quality_2"] = round(q2, 2)

        # Similarity scores
        hist_score   = self._histogram_similarity(face1, face2)
        ssim_score   = self._ssim_similarity(face1, face2)
        feat_score   = self._feature_similarity(face1, face2)

        result["histogram_score"] = round(hist_score, 2)
        result["ssim_score"]      = round(ssim_score, 2)
        result["feature_score"]   = round(feat_score, 2)

        # Weighted blend
        final = (
            hist_score * self.WEIGHTS["histogram"] +
            ssim_score * self.WEIGHTS["ssim"] +
            feat_score * self.WEIGHTS["feature"]
        )
        final = max(0.0, min(100.0, final))

        result["similarity_score"] = round(final, 2)
        result["match_status"] = "Match" if final >= self.threshold else "No Match"
        result["match_label"]  = self._classify(final)
        result["confidence"]   = round(abs(final - self.threshold) / self.threshold * 100, 1)
        result["processing_time"] = round(time.perf_counter() - t0, 4)

        return result

    # ── helpers ─────────────────────────────────────────────────────────────────

    def _load_image(self, path: str) -> Optional[np.ndarray]:
        try:
            img = cv2.imread(path)
            if img is None:
                return None
            return img
        except Exception:
            return None

    def _extract_face(self, img: np.ndarray) -> Tuple[np.ndarray, float, Optional[str]]:
        """Returns (cropped_face_normalized, quality_score, error_str)."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if self._face_cascade is not None:
            faces = self._face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            if len(faces) == 0:
                # Soft fallback: use full image
                face_img = img
            elif len(faces) > 1:
                # Use largest detected face
                faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                x, y, w, h = faces[0]
                face_img = img[y:y+h, x:x+w]
            else:
                x, y, w, h = faces[0]
                face_img = img[y:y+h, x:x+w]
        else:
            face_img = img   # No cascade available, use full image

        # Normalize to fixed size
        face_resized = cv2.resize(face_img, self.FACE_SIZE)
        quality = self._face_quality(gray)
        return face_resized, quality, None

    def _face_quality(self, gray: np.ndarray) -> float:
        """Laplacian-based sharpness score mapped to 0–100."""
        lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        score = min(100.0, lap_var / 5.0)
        return round(score, 2)

    def _histogram_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Compare HSV channel histograms; return 0–100."""
        h1 = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
        h2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
        scores = []
        for ch in range(3):
            hist1 = cv2.calcHist([h1], [ch], None, [64], [0, 256])
            hist2 = cv2.calcHist([h2], [ch], None, [64], [0, 256])
            cv2.normalize(hist1, hist1)
            cv2.normalize(hist2, hist2)
            score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            scores.append(max(0.0, score))
        return sum(scores) / len(scores) * 100.0

    def _ssim_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Structural similarity on grayscale faces; return 0–100."""
        g1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        g2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

        if SKIMAGE_AVAILABLE:
            score = ssim(g1, g2, data_range=1.0)
        else:
            score = self._manual_ssim(g1, g2)

        return max(0.0, score * 100.0)

    def _manual_ssim(self, a: np.ndarray, b: np.ndarray) -> float:
        """Simplified SSIM without skimage."""
        C1, C2 = (0.01**2), (0.03**2)
        mu_a, mu_b = a.mean(), b.mean()
        sig_a = np.std(a)
        sig_b = np.std(b)
        sig_ab = np.mean((a - mu_a) * (b - mu_b))
        num = (2*mu_a*mu_b + C1) * (2*sig_ab + C2)
        den = (mu_a**2 + mu_b**2 + C1) * (sig_a**2 + sig_b**2 + C2)
        return float(num / den) if den != 0 else 0.0

    def _feature_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        LBP-inspired texture feature vector cosine similarity; return 0–100.
        """
        def lbp_hist(img: np.ndarray) -> np.ndarray:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.uint8)
            rows, cols = gray.shape
            result = np.zeros_like(gray)
            for dy, dx in [(-1,-1),(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1)]:
                shifted = np.roll(np.roll(gray, dy, axis=0), dx, axis=1)
                result = (result << 1) | (gray >= shifted).astype(np.uint8)
            hist, _ = np.histogram(result.ravel(), bins=256, range=(0,256))
            return hist.astype(np.float32)

        v1 = lbp_hist(img1)
        v2 = lbp_hist(img2)
        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)
        if n1 == 0 or n2 == 0:
            return 0.0
        cosine = np.dot(v1, v2) / (n1 * n2)
        return max(0.0, float(cosine) * 100.0)

    @staticmethod
    def _classify(score: float) -> str:
        if score >= 90: return "Excellent Match"
        if score >= 75: return "Strong Match"
        if score >= 60: return "Possible Match"
        if score >= 40: return "Weak Match"
        return "No Match"
