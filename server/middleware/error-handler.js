"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.errorHandler = errorHandler;
const errors_1 = require("../types/errors");
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function errorHandler(err, _req, res, next) {
    console.error("Error:", err.message);
    let statusCode = 500;
    let errorMessage = "Internal server error";
    if (err instanceof errors_1.StockCodeError) {
        statusCode = 400;
        errorMessage = err.message;
    }
    else if (err instanceof errors_1.StockRequestError) {
        statusCode = 502;
        errorMessage = err.message;
    }
    else if (err instanceof errors_1.StockParseError) {
        statusCode = 500;
        errorMessage = err.message;
    }
    else if (err instanceof errors_1.StockApiError) {
        statusCode = 500;
        errorMessage = err.message;
    }
    res.status(statusCode).json({
        success: false,
        error: errorMessage,
    });
}
//# sourceMappingURL=error-handler.js.map