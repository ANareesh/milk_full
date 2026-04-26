import axios from "axios";
export const submitFeedback = (message, token) =>
  axios.post("/api/v1/feedback/", { message }, {
    headers: { Authorization: `Bearer ${token}` },
  });