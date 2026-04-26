import axios from "axios";
export const createBatch = (batchCode, token) =>
  axios.post("/api/v1/batch/", { batch_code: batchCode }, {
    headers: { Authorization: `Bearer ${token}` },
  });