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

        if (!res.ok) {
          setApiError(`Failed to load (HTTP ${res.status})`);
          return;
        }

        setCriminals((data.criminals || []).filter((c) => c?.imageURL));
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
        
        {/* LEFT SECTION */}
        <div className={styles.left}>
          {/* <h2 className={styles.title}>About this website</h2>
          <p className={styles.lead}>
            This system generates faces, matches them with a criminal database,
            and allows secure enrollment of records.
          </p> */}

          <div className={styles.points}>

            {/* ABOUT */}
            <div className={styles.cardBox}>
              <div className={styles.cardTitle2}>🔍 About Project</div>
              <p>
                AI-based facial recognition using deep learning embeddings 
                to identify individuals from a criminal database.
              </p>
              <p>
                Enables secure enrollment, fast matching, and real-time identification.
              </p>
            </div>

            {/* TITLE */}
            <div className={styles.cardBox}>
              <div className={styles.cardTitle2}>📌 Project Title</div>
              <p><b>Criminal Face Generation and Recognition</b></p>
            </div>

            {/* DEVELOPERS */}
            <div className={styles.cardBox}>
              <div className={styles.cardTitle2}>👨‍💻 Developers</div>

              <div className={styles.devRow}>
                <span>Anshul Rajpoot</span>
                <span>2311401168</span>
              </div>
              <div className={styles.devRow}>
                <span>Satyam Gupta</span>
                <span>2311401167</span>
              </div>
              <div className={styles.devRow}>
                <span>Ritesh Jat</span>
                <span>2311401165</span>
              </div>
              <div className={styles.devRow}>
                <span>Gajendra Verma</span>
                <span>2311401211</span>
              </div>
            </div>

            {/* COLLEGE */}
            <div className={styles.cardBox}>
              <div className={styles.cardTitle2}>🎓 Institution</div>
              <p>MANIT Bhopal</p>
              <p>Electronics & Communication Engineering (ECE)</p>
            </div>

            {/* MENTOR */}
            <div className={styles.cardBox}>
              <div className={styles.cardTitle2}>🧑‍🏫 Project Mentor</div>
              <p>Dr. Manish Kashyap</p>
            </div>

          </div>
        </div>

        {/* RIGHT SECTION */}
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

              {active?.name && (
                <div className={styles.overlay}>
                  <div className={styles.name}>{active.name}</div>
                  <div className={styles.meta}>
                    {active.sex && `• ${active.sex}`}
                    {active.crime && ` • ${active.crime}`}
                  </div>
                </div>
              )}
            </div>

            {criminals.length > 1 && (
              <div className={styles.dots}>
                {criminals.slice(0, 8).map((_, i) => (
                  <span
                    key={i}
                    className={i === activeIndex ? styles.dotActive : styles.dot}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}