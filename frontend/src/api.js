import axios from 'axios'

// Points at the local FastAPI backend (uvicorn app.main:app --reload).
// Change this if the backend runs somewhere else.
const BASE_URL = 'http://localhost:8000/api/v1'

const client = axios.create({ baseURL: BASE_URL, timeout: 60000 })

// Each function returns { data } on success, or throws with a normalized
// error message pulled from FastAPI's {detail: "..."} error shape - so
// components don't need to know the difference between a 500, 503, or
// network failure, they just get a readable string either way.
function unwrapError(error) {
  if (error.response?.data?.detail) {
    return new Error(error.response.data.detail)
  }
  if (error.code === 'ECONNABORTED') {
    return new Error('Request timed out - the model may still be loading on first use.')
  }
  return new Error('Could not reach the backend. Is it running on http://localhost:8000?')
}

export async function analyzeSentiment(text) {
  try {
    const { data } = await client.post('/sentiment/analyze', { text })
    return data
  } catch (e) {
    throw unwrapError(e)
  }
}

export async function analyzeCredibility(text, sourceName, url) {
  try {
    const { data } = await client.post('/credibility/analyze', {
      text,
      source_name: sourceName || null,
      url: url || null,
    })
    return data
  } catch (e) {
    throw unwrapError(e)
  }
}

export async function findSimilarArticles(text, topK = 5) {
  try {
    const { data } = await client.post('/retrieval/similar-articles', { text, top_k: topK })
    return data
  } catch (e) {
    throw unwrapError(e)
  }
}

export async function analyzeConsensus(text, topK = 5) {
  try {
    const { data } = await client.post('/consensus/analyze', { text, top_k: topK })
    return data
  } catch (e) {
    throw unwrapError(e)
  }
}
