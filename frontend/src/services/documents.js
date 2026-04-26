import axios from "axios";

export const uploadDocument = (docType, file, token) => {
  const formData = new FormData();
  formData.append("doc_type", docType);
  formData.append("file", file);
  return axios.post("/api/v1/documents/upload", formData, {
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "multipart/form-data" },
  });
};