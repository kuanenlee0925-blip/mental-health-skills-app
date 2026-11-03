export async function api(path, options = {}) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 40000)
  try {
    const response = await fetch('/api' + path, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options.headers },
      signal: controller.signal,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    })
    let data
    try { data = await response.json() } catch { throw new Error('The local service is unavailable. You can retry.') }
    if (!response.ok) throw new Error(data.error?.message || 'This operation could not be completed.')
    return data
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('The request timed out. Saving is not confirmed; you can retry.')
    if (error instanceof TypeError) throw new Error('The local service is unavailable. Saving is not confirmed; you can retry.')
    throw error
  } finally {
    clearTimeout(timeout)
  }
}
