import { useState, useEffect } from "react";
import { apiUrl } from "../utils/api.js";

export default function AdminUpload() {
  const [form, setForm] = useState({
    name: "",
    age: "",
    sex: "",
    address: "",
    height: "",
    weight: "",
    crime: "",
    status: "ARRESTED",
  });

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (key, value) => {
    setForm({ ...form, [key]: value });
  };

  // ✅ prevent memory leak
  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  const handleUpload = async () => {
    if (!file) return alert("Upload image");

    const formData = new FormData();
    Object.entries(form).forEach(([k, v]) => formData.append(k, v));
    formData.append("image", file);

    const token = localStorage.getItem("token");

    try {
      setLoading(true);

      const res = await fetch(apiUrl("/api/enroll"), {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) return alert(data.message);

      alert("✅ Criminal Added");

      setForm({
        name: "",
        age: "",
        sex: "",
        address: "",
        height: "",
        weight: "",
        crime: "",
        status: "ARRESTED",
      });

      setFile(null);
      setPreview(null);
    } catch {
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>

        {/* LEFT PANEL */}
        <div style={styles.leftPanel}>
          {preview ? (
            <img src={preview} alt="preview" style={styles.previewImgLarge} />
          ) : (
            <div style={styles.previewPlaceholder}>
              📸 Upload Image to Preview
            </div>
          )}
        </div>

        {/* RIGHT PANEL */}
        <div style={styles.rightPanel}>
          <h2 style={styles.title}>🚨 Add Criminal</h2>

          <div style={styles.grid}>
            <input style={styles.input} placeholder="Name" value={form.name} onChange={(e) => handleChange("name", e.target.value)} />
            <input style={styles.input} type="number" placeholder="Age" value={form.age} onChange={(e) => handleChange("age", e.target.value)} />

            <select style={styles.select} value={form.sex} onChange={(e) => handleChange("sex", e.target.value)}>
              <option value="">Gender</option>
              <option>Male</option>
              <option>Female</option>
            </select>

            <input style={styles.input} placeholder="Address" value={form.address} onChange={(e) => handleChange("address", e.target.value)} />

            <input style={styles.input} type="number" placeholder="Height (cm)" value={form.height} onChange={(e) => handleChange("height", e.target.value)} />
            <input style={styles.input} type="number" placeholder="Weight (kg)" value={form.weight} onChange={(e) => handleChange("weight", e.target.value)} />

            <input style={styles.input} placeholder="Crime" value={form.crime} onChange={(e) => handleChange("crime", e.target.value)} />
          </div>

          {/* STATUS */}
          <div style={styles.status}>
            <button
              style={form.status === "ARRESTED" ? styles.activeBtn : styles.btn}
              onClick={() => handleChange("status", "ARRESTED")}
            >
              Arrested
            </button>

            <button
              style={form.status === "NOT ARRESTED" ? styles.activeBtn : styles.btn}
              onClick={() => handleChange("status", "NOT ARRESTED")}
            >
              Not Arrested
            </button>
          </div>

          {/* FILE */}
          <input
            style={{ marginTop: "15px", color: "white" }}
            type="file"
            accept=".jpg,.png"
            onChange={(e) => {
              const f = e.target.files[0];
              setFile(f);
              setPreview(URL.createObjectURL(f));
            }}
          />

          {/* SUBMIT */}
          <button style={styles.submit} onClick={handleUpload}>
            {loading ? "Adding..." : "➕ Add Criminal"}
          </button>
        </div>

      </div>
    </div>
  );
}

const styles = {
  page: {
    height: "100vh",
    width: "100vw",
    background: "linear-gradient(to right, #020617, #0f172a)",
  },

  container: {
    display: "flex",
    width: "100%",
    height: "100%",
  },

  leftPanel: {
    flex: 0.7,
    background: "#020617",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },

  previewImgLarge: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
  },

  previewPlaceholder: {
    color: "#64748b",
    fontSize: "22px",
  },

  rightPanel: {
    flex: 1,
    background: "#1e293b",
    padding: "30px",
    overflowY: "auto",
  },

  title: {
    marginBottom: "20px",
    fontSize: "24px",
    textAlign: "center",
    color: "#fff",
  },

  grid: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    alignItems: "center",
  },

  input: {
    width: "85%",
    padding: "14px",
    borderRadius: "10px",
    border: "none",
    background: "#e2e8f0",
    color: "#0f172a",
    fontSize: "14px",
  },

  select: {
    width: "85%",
    padding: "14px",
    borderRadius: "10px",
    border: "none",
    background: "#e2e8f0",
    color: "#0f172a",
  },

  status: {
    display: "flex",
    gap: "10px",
    marginTop: "15px",
  },

  btn: {
    flex: 1,
    padding: "12px",
    background: "#334155",
    border: "none",
    borderRadius: "8px",
    color: "#fff",
    cursor: "pointer",
  },

  activeBtn: {
    flex: 1,
    padding: "12px",
    background: "#3b82f6",
    borderRadius: "8px",
    color: "#fff",
    fontWeight: "bold",
    border: "none",
  },

  submit: {
    marginTop: "20px",
    padding: "14px",
    borderRadius: "10px",
    background: "linear-gradient(135deg,#6366f1,#3b82f6)",
    color: "#fff",
    fontWeight: "bold",
    border: "none",
    cursor: "pointer",
    width: "85%",
    display: "block",
    marginLeft: "auto",
    marginRight: "auto",
  },
};