import styles from "./AppFooter.module.css";

export default function AppFooter() {
  return (
    <footer className={styles.footer} id="app-footer">
      <div className={styles.inner}>
        <div className={styles.brandCol}>
          <div className={styles.brandRow}>
            <img
              src="/assets/logo.png"
              className={styles.brandLogo}
              alt="Face Generator"
            />
            <div className={styles.brandName}>Face Generator</div>
          </div>

          <div className={styles.followWrap}>
            <div className={styles.followTitle}>Follow us</div>
            <div className={styles.socialRow}>
              <a className={styles.socialBtn} href="#" aria-label="X">
                X
              </a>
              <a className={styles.socialBtn} href="#" aria-label="LinkedIn">
                in
              </a>
              <a className={styles.socialBtn} href="#" aria-label="Instagram">
                ig
              </a>
              <a className={styles.socialBtn} href="#" aria-label="GitHub">
                gh
              </a>
              <a className={styles.socialBtn} href="#" aria-label="RSS">
                rss
              </a>
            </div>
          </div>
        </div>

        <div className={styles.col} id="help">
          <div className={styles.colTitle}>About this app</div>
          <a className={styles.colLink} href="#">Privacy notice</a>
          <a className={styles.colLink} href="#">Cookies</a>
          <a className={styles.colLink} href="#">Accessibility</a>
          <a className={styles.colLink} href="#">Terms &amp; conditions</a>
          <a className={styles.colLink} href="#">Social media policy</a>
        </div>

        <div className={styles.col} id="contact">
          <div className={styles.colTitle}>Contact</div>
          <a className={styles.colLink} href="#">Report an issue</a>
          <a className={styles.colLink} href="#">Report suspicious profile</a>
          <a className={styles.colLink} href="#">Verify a contact</a>
          <a className={styles.colLink} href="#">Report a vulnerability</a>
          <a className={styles.colLink} href="#">Contact the press office</a>
          <a className={styles.colLink} href="#">Can't find what you're looking for?</a>
        </div>

        <div className={styles.col} id="links">
          <div className={styles.colTitle}>Useful links</div>
          <a className={styles.colLink} href="#">Documentation</a>
          <a className={styles.colLink} href="#">API status</a>
          <a className={styles.colLink} href="#">Security</a>
          <a className={styles.colLink} href="#">Support</a>
          <a className={styles.colLink} href="#">Gov portal</a>
        </div>
      </div>

      <div className={styles.bottom}>
        <span className={styles.muted}>
          © {new Date().getFullYear()} Face Generator
        </span>
      </div>
    </footer>
  );
}
