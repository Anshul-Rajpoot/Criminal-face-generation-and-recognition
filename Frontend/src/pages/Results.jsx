import { useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import styles from "./Results.module.css";

function dataUrlToFile(dataUrl, filename) {
  const [meta, b64] = dataUrl.split(",");
  const mime = meta.match(/data:(.*);base64/)?.[1] || "image/png";
  const bin = atob(b64);
  const buf = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
  const blob = new Blob([buf], { type: mime });
  return new File([blob], filename, { type: mime });
}

async function dataUrlToSearchFile(dataUrl, filename) {
  // Make the generated image more compatible with face-recognition models:
  // - remove transparency by drawing on a white background
  // - upscale to a square canvas so the face occupies more pixels
  const img = new Image();
  img.src = dataUrl;
  img.crossOrigin = "anonymous";
  await new Promise((resolve, reject) => {
    img.onload = resolve;
    img.onerror = reject;
  });

  const size = 512;
  const c = document.createElement("canvas");
  c.width = size;
  c.height = size;
  const ctx = c.getContext("2d");
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, size, size);

  const scale = Math.min(size / img.width, size / img.height);
  const dw = Math.round(img.width * scale);
  const dh = Math.round(img.height * scale);
  const dx = Math.round((size - dw) / 2);
  const dy = Math.round((size - dh) / 2);
  ctx.drawImage(img, dx, dy, dw, dh);

  const blob = await new Promise((resolve) =>
    c.toBlob(resolve, "image/jpeg", 0.95),
  );
  return new File([blob], filename, { type: blob.type || "image/jpeg" });
}

export default function Results() {
  const location = useLocation();
  const API_BASE = useMemo(() => "http://localhost:8000", []);

  const [generatedImageUrl, setGeneratedImageUrl] = useState(() => {
    return (
      location.state?.generatedImageUrl ||
      sessionStorage.getItem("generatedImageUrl") ||
      null
    );
  });

  const [gender, setGender] = useState(() => {
    return location.state?.gender || sessionStorage.getItem("generatedGender") || "Any";
  });

  const [loading, setLoading] = useState(false);
  const [matches, setMatches] = useState([]);
  const [autoSearched, setAutoSearched] = useState(false);

  useEffect(() => {
    if (location.state?.generatedImageUrl) {
      sessionStorage.setItem("generatedImageUrl", location.state.generatedImageUrl);
      setGeneratedImageUrl(location.state.generatedImageUrl);
    }
    if (location.state?.gender) {
      sessionStorage.setItem("generatedGender", location.state.gender);
      setGender(location.state.gender);
    }
  }, [location.state]);

  const runSearch = async (e) => {
    e?.preventDefault?.();

    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please login first");
      return;
    }

    const imageFile = generatedImageUrl
      ? await dataUrlToSearchFile(generatedImageUrl, `generated-${Date.now()}.jpg`)
      : null;

    if (!imageFile) {
      alert("Please generate an image first");
      return;
    }

    const formData = new FormData();
    formData.append("image", imageFile);
    if (gender && gender !== "Any") formData.append("sex_filter", gender);
    // If the generated image doesn't clear the strict threshold, still return the
    // best candidates so the user can iterate.
    formData.append("include_candidates", "1");

    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        alert(data.error || data.message || "Search failed");
        setMatches([]);
        return;
      }

      const sorted = (data.matches || []).sort((a, b) => b.score - a.score);
      setMatches(sorted);
    } catch (err) {
      alert("Server error");
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!autoSearched && generatedImageUrl) {
      setAutoSearched(true);
      runSearch();
    }
  }, [autoSearched, generatedImageUrl]);

  return (
    <div className={styles.page}>
      <div className={styles.layout}>
        <section className={styles.left}>
          <div className={styles.card}>
            <h2 className={styles.cardTitle}>Generated Image</h2>

            {generatedImageUrl ? (
              <img className={styles.generatedImg} src={generatedImageUrl} alt="Generated" />
            ) : (
              <p className={styles.muted}>No generated image yet.</p>
            )}
          </div>
        </section>

        <section className={styles.right}>
          <div className={styles.card}>
            <h2 className={styles.cardTitle}>Search Face</h2>

            <form className={styles.searchForm} onSubmit={runSearch}>
              <button className={styles.primaryBtn} type="submit" disabled={loading}>
                {loading ? "Searching..." : "Search"}
              </button>
            </form>

            <div className={styles.resultsScroll}>
              {matches.length > 0 ? (
               <div className={styles.resultsGrid}>
  {matches.slice(0, 12).map((m, i) => (
    <div
      key={`${m.name}-${i}`}
      className={i === 0 ? styles.resultCardBest : styles.resultCard}
    >
      {m.imageURL && (
        <div className={styles.imgWrapper}>
          <img
            className={styles.resultImg}
            src={m.imageURL}
            alt={m.name || "match"}
          />
        </div>
      )}

      <p className={styles.matchLine}>
        Match:{" "}
        {typeof m.score === "number"
          ? `${(m.score * 100).toFixed(1)}%`
          : "-"}
      </p>

      <p className={styles.nameLine}>{m.name}</p>

      {m.age != null && <p className={styles.metaLine}>Age: {m.age}</p>}
      {m.sex && <p className={styles.metaLine}>Sex: {m.sex}</p>}
      {m.crime && <p className={styles.metaLine}>Crime: {m.crime}</p>}
      {m.status && <p className={styles.metaLine}>Status: {m.status}</p>}
    </div>
  ))}
</div>
              ) : (
                !loading && (
                  <p className={styles.muted}>
                    {generatedImageUrl ? "No matches yet." : "Generate an image to search."}
                  </p>
                )
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
