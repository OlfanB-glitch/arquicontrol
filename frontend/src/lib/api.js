import axios from "axios";

const api = axios.create({
  baseURL: `${process.env.REACT_APP_BACKEND_URL}/api`,
});

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    return;
  }

  delete api.defaults.headers.common.Authorization;
}

export async function openDocumentResource(url) {
  if (!url) return;

  if (!url.startsWith("/api/")) {
    window.open(url, "_blank", "noopener,noreferrer");
    return;
  }

  const response = await api.get(url, { responseType: "blob" });
  const objectUrl = window.URL.createObjectURL(response.data);
  window.open(objectUrl, "_blank", "noopener,noreferrer");
  window.setTimeout(() => window.URL.revokeObjectURL(objectUrl), 30000);
}

export async function downloadApiFile(url, fallbackFilename = "reporte") {
  const response = await api.get(url, { responseType: "blob" });
  const disposition = response.headers?.["content-disposition"] || "";
  const match = disposition.match(/filename="?([^";]+)"?/i);
  const filename = match?.[1] || fallbackFilename;
  const objectUrl = window.URL.createObjectURL(response.data);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => window.URL.revokeObjectURL(objectUrl), 30000);
}

export default api;