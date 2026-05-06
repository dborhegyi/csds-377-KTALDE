/**
 * Color utility functions for LAMPI web interface
 *
 * These functions convert between color spaces (HSB to RGB to Hex)
 * and are used for dynamically styling slider thumbs and the color box.
 */

/**
 * Convert HSB (Hue, Saturation, Brightness) to RGB
 * @param {number} h - Hue (0-360)
 * @param {number} s - Saturation (0-1)
 * @param {number} b - Brightness (0-1)
 * @returns {Object} - { r, g, b } values (0-255)
 */
export function hsbToRgb(h, s, b) {
  h = h % 360;
  const c = b * s;
  const x = c * (1 - Math.abs((h / 60) % 2 - 1));
  const m = b - c;

  let r, g, bl;
  if (h < 60) {
    r = c; g = x; bl = 0;
  } else if (h < 120) {
    r = x; g = c; bl = 0;
  } else if (h < 180) {
    r = 0; g = c; bl = x;
  } else if (h < 240) {
    r = 0; g = x; bl = c;
  } else if (h < 300) {
    r = x; g = 0; bl = c;
  } else {
    r = c; g = 0; bl = x;
  }

  return {
    r: Math.round((r + m) * 255),
    g: Math.round((g + m) * 255),
    b: Math.round((bl + m) * 255)
  };
}

/**
 * Convert RGB to hex color string
 * @param {number} r - Red (0-255)
 * @param {number} g - Green (0-255)
 * @param {number} b - Blue (0-255)
 * @returns {string} - Hex color string (e.g., "#ff0000")
 */
export function rgbToHex(r, g, b) {
  return '#' + [r, g, b].map(x => {
    const hex = x.toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  }).join('');
}

/**
 * Convert HSB to hex color string (convenience function)
 * @param {number} h - Hue (0-360)
 * @param {number} s - Saturation (0-1)
 * @param {number} b - Brightness (0-1)
 * @returns {string} - Hex color string
 */
export function hsbToHex(h, s, b) {
  const rgb = hsbToRgb(h, s, b);
  return rgbToHex(rgb.r, rgb.g, rgb.b);
}

/**
 * Darken a hex color by a percentage (for slider thumb borders)
 * @param {string} hex - Hex color string
 * @param {number} percent - Amount to darken (0-100)
 * @returns {string} - Darkened hex color string
 */
export function darkenHex(hex, percent) {
  const num = parseInt(hex.slice(1), 16);
  const amt = Math.round(2.55 * percent);
  const r = Math.max(0, (num >> 16) - amt);
  const g = Math.max(0, ((num >> 8) & 0x00ff) - amt);
  const b = Math.max(0, (num & 0x0000ff) - amt);
  return rgbToHex(r, g, b);
}
