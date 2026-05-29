javascript
// server/utils/aiAnalyzer.js

const tf = require('@tensorflow/tfjs-node');
const natural = require('natural');
const { extractTextFromPDF, extractTextFromImage } = require('./fileHandler');

/**
 * Analyze the extracted text from medical reports to identify key health indicators.
 * @param {Buffer} fileBuffer - The buffer of the uploaded file.
 * @param {string} fileType - The type of the file ('pdf' or 'image').
 * @returns {Promise<Object>} - An object containing extracted values and risk analysis.
 */
async function analyzeReport(fileBuffer, fileType) {
    let extractedText;
    
    try {
        if (fileType === 'pdf') {
            extractedText = await extractTextFromPDF(fileBuffer);
        } else if (fileType === 'image') {
            extractedText = await extractTextFromImage(fileBuffer);
        } else {
            throw new Error('Unsupported file type');
        }
    } catch (error) {
        throw new Error('Error extracting text from file: ' + error.message);
    }

    const keyValues = extractKeyValues(extractedText);
    const riskLevel = analyzeRiskLevel(keyValues);

    return {
        keyValues,
        riskLevel
    };
}

/**
 * Extract key health indicators from the text.
 * @param {string} text - The extracted text from the medical report.
 * @returns {Object} - An object containing key health indicators.
 */
function extractKeyValues(text) {
    const tokenizer = new natural.WordTokenizer();
    const tokens = tokenizer.tokenize(text.toLowerCase());

    const keyValues = {
        glucose: findValue(tokens, 'glucose'),
        cholesterol: findValue(tokens, 'cholesterol'),
        tsh: findValue(tokens, 'tsh')
    };

    return keyValues;
}

/**
 * Find the value associated with a specific health indicator in the tokens.
 * @param {string[]} tokens - Tokenized words from the report.
 * @param {string} key - The health indicator to find.
 * @returns {number|null} - The extracted value or null if not found.
 */
function findValue(tokens, key) {
    const index = tokens.indexOf(key);
    if (index !== -1 && tokens[index + 1] === ':') {
        const value = parseFloat(tokens[index + 2]);
        return isNaN(value) ? null : value;
    }
    return null;
}

/**
 * Analyze the risk level based on extracted key values.
 * @param {Object} keyValues - The extracted key health indicators.
 * @returns {string} - The risk level ('Low', 'Medium', 'High').
 */
function analyzeRiskLevel(keyValues) {
    const { glucose, cholesterol, tsh } = keyValues;
    let riskScore = 0;

    if (glucose !== null) {
        riskScore += glucose > 125 ? 2 : glucose > 100 ? 1 : 0;
    }
    if (cholesterol !== null) {
        riskScore += cholesterol > 240 ? 2 : cholesterol > 200 ? 1 : 0;
    }
    if (tsh !== null) {
        riskScore += tsh > 4.0 ? 2 : tsh > 2.5 ? 1 : 0;
    }

    if (riskScore >= 5) return 'High';
    if (riskScore >= 3) return 'Medium';
    return 'Low';
}

module.exports = {
    analyzeReport
};