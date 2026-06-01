const express = require("express");
const apiRouter = require("./routes").default;
const eh = require("./middleware/error-handler");

const app = express();
const PORT = process.env.PROXY_PORT || 3001;

app.use(express.json());
app.use("/api", apiRouter);
app.use(eh.errorHandler);

app.listen(PORT, () => {
  console.log(`[proxy] Stock API server running at http://localhost:${PORT}`);
});
