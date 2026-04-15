
import { useEffect, useRef, useState } from "react";
import { apiUrl } from "../utils/api.js";
import styles from "./Home.module.css";

export default function Home() {
  const [criminals, setCriminals] = useState([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [fadeIn, setFadeIn] = useState(true);
  const [apiError, setApiError] = useState("");

  const timerRef = useRef(null);

  useEffect(() => {
    const run = async () => {
      try {
        const res = await fetch(apiUrl("/api/latest-criminals?limit=10"));
        const data = await res.json();

        console.log("API DATA:", data); // 🔥 DEBUG

        if (!res.ok) {
          setApiError(`Failed to load (HTTP ${res.status})`);
          return;
        }

        // ✅ FIXED HERE
        const list = Array.isArray(data) ? data : [];
        setCriminals(list.filter((c) => c?.imageURL));
      } catch {
        setApiError("Backend not reachable");
      }
    };

    run();
  }, []);

  useEffect(() => {
    if (!criminals.length) return;

    if (timerRef.current) clearInterval(timerRef.current);

    timerRef.current = setInterval(() => {
      setFadeIn(false);
      setTimeout(() => {
        setActiveIndex((prev) => (prev + 1) % criminals.length);
        setFadeIn(true);
      }, 200);
    }, 3000);

    return () => clearInterval(timerRef.current);
  }, [criminals]);

  const active = criminals[activeIndex];

  return (
    <div className={styles.page}>
      <div className={styles.hero}>
        <div className={styles.left}>
          <div className={styles.points}>
            <div className={styles.cardBox}>
              <div className={styles.cardTitle2}>🔍 About Project</div>
              <p>
                AI-based facial recognition using deep learning embeddings
                to identify individuals from a criminal database.
              </p>
            </div>
          </div>
        </div>

        <div className={styles.right}>
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <h3 className={styles.cardTitle}>Most Wanted</h3>
            </div>

            <div className={styles.frame}>
              {active?.imageURL ? (
                <img
                  src={active.imageURL}
                  alt={active.name}
                  className={fadeIn ? styles.imgIn : styles.imgOut}
                />
              ) : (
                <div className={styles.placeholder}>
                  {apiError || "No data available"}
                </div>
              )}
            </div>

            {active?.name && (
              <div className={styles.overlay}>
                <div className={styles.name}>{active.name}</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

