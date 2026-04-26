import React, { useState } from "react";
import { uploadDocument } from "../services/documents";
import { useAuth } from "../context/AuthContext";

const DocumentUpload = () => {
  const { token } = useAuth();
  const [file, setFile] = useState(null);
  const [docType, setDocType] = useState("KYC");
  const [msg, setMsg] = useState("");

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    const res = await uploadDocument(docType, file, token);
    setMsg(res.data.msg);
  };

  return (
    <form onSubmit={handleUpload}>
      <select value={docType} onChange={e => setDocType(e.target.value)}>
        <option value="KYC">KYC</option>
        <option value="contract">Contract</option>
      </select>
      <input type="file" onChange={e => setFile(e.target.files[0])} />
      <button type="submit">Upload</button>
      {msg && <div>{msg}</div>}
    </form>
  );
};

export default DocumentUpload;