// Interactive Elements for Iglesia Presbiteriana de Macaé Landing Page

document.addEventListener("DOMContentLoaded", () => {
  setupPixCopy();
  setupLightbox();
});

/**
 * Copies the PIX CNPJ key to clipboard and displays a feedback tooltip.
 */
function setupPixCopy() {
  const copyBtn = document.getElementById("btn-copy-pix");
  const pixKeyVal = document.getElementById("pix-key-val");

  if (!copyBtn || !pixKeyVal) return;

  copyBtn.addEventListener("click", async () => {
    // Extract key and remove any trailing/leading whitespaces
    const textToCopy = pixKeyVal.textContent.trim();

    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(textToCopy);
      } else {
        // Fallback for older browsers or non-secure contexts
        const textarea = document.createElement("textarea");
        textarea.value = textToCopy;
        textarea.style.position = "fixed"; // Avoid scrolling to bottom
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
      }

      // Show copied tooltip feedback and toggle SVG icons
      const iconCopy = copyBtn.querySelector(".icon-copy");
      const iconCheck = copyBtn.querySelector(".icon-check");
      
      copyBtn.classList.add("copied");
      if (iconCopy && iconCheck) {
        iconCopy.style.display = "none";
        iconCheck.style.display = "block";
      }
      
      setTimeout(() => {
        copyBtn.classList.remove("copied");
        if (iconCopy && iconCheck) {
          iconCopy.style.display = "block";
          iconCheck.style.display = "none";
        }
      }, 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  });
}

/**
 * Handles image lightbox interactions for the "Vida em Comunidade" gallery.
 */
function setupLightbox() {
  const lightbox = document.getElementById("lightbox");
  const lightboxImg = document.getElementById("lightbox-img");
  const closeBtn = document.getElementById("lightbox-close");
  const galleryItems = document.querySelectorAll(".gallery-item");

  if (!lightbox || !lightboxImg || !closeBtn) return;

  // Open Lightbox on item click
  galleryItems.forEach(item => {
    item.addEventListener("click", () => {
      const src = item.getAttribute("data-src");
      const alt = item.querySelector("img")?.getAttribute("alt") || "Imagem ampliada";
      
      if (src) {
        lightboxImg.src = src;
        lightboxImg.alt = alt;
        lightbox.classList.add("active");
        document.body.style.overflow = "hidden"; // Disable scroll when active
      }
    });
  });

  // Close Lightbox on close button click
  closeBtn.addEventListener("click", () => {
    closeLightbox();
  });

  // Close Lightbox on clicking outside the image content
  lightbox.addEventListener("click", (e) => {
    if (e.target === lightbox) {
      closeLightbox();
    }
  });

  // Close Lightbox on Escape key press
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && lightbox.classList.contains("active")) {
      closeLightbox();
    }
  });

  function closeLightbox() {
    lightbox.classList.remove("active");
    document.body.style.overflow = ""; // Re-enable scroll
    setTimeout(() => {
      lightboxImg.src = "";
    }, 300); // Clear src after fade-out transition
  }
}
