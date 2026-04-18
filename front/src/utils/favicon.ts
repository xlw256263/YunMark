/**
 * Favicon 获取与缓存工具
 *
 * 采用多源降级策略获取网站图标，并使用 localStorage 缓存结果。
 */

/**
 * Favicon 缓存接口
 */
interface FaviconCacheEntry {
  /** 图标 URL */
  url: string
  /** 缓存时间戳 */
  cachedAt: number
  /** 域名 */
  domain: string
}

/**
 * Favicon 缓存配置
 */
const FAVICON_CACHE_CONFIG = {
  /** 缓存键前缀 */
  CACHE_KEY_PREFIX: 'favicon_cache_',
  /** 缓存有效期（30 天，从 7 天延长） */
  CACHE_TTL: 30 * 24 * 60 * 60 * 1000,
  /** 请求超时时间（3 秒） */
  REQUEST_TIMEOUT: 3000,
}

/**
 * 全局请求缓存：防止同一域名的重复请求
 * Key: domain, Value: Promise<string | null>
 */
const pendingRequests = new Map<string, Promise<string | null>>()

/**
 * 获取域名
 * @param url - 完整 URL
 * @returns 域名（不含协议）
 */
export function getDomain(url: string): string {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname
  } catch {
    return ''
  }
}

/**
 * 从 localStorage 获取缓存的 Favicon
 * @param domain - 域名
 * @returns 缓存的图标 URL 或 null
 */
export function getCachedFavicon(domain: string): string | null {
  try {
    const cacheKey = `${FAVICON_CACHE_CONFIG.CACHE_KEY_PREFIX}${domain}`
    const cached = localStorage.getItem(cacheKey)

    if (!cached) return null

    const entry: FaviconCacheEntry = JSON.parse(cached)
    const now = Date.now()

    // 检查缓存是否过期
    if (now - entry.cachedAt > FAVICON_CACHE_CONFIG.CACHE_TTL) {
      localStorage.removeItem(cacheKey)
      return null
    }

    return entry.url
  } catch {
    return null
  }
}

/**
 * 缓存 Favicon 到 localStorage
 * @param domain - 域名
 * @param url - 图标 URL
 */
export function cacheFavicon(domain: string, url: string): void {
  try {
    const cacheKey = `${FAVICON_CACHE_CONFIG.CACHE_KEY_PREFIX}${domain}`
    const entry: FaviconCacheEntry = {
      url,
      cachedAt: Date.now(),
      domain,
    }
    localStorage.setItem(cacheKey, JSON.stringify(entry))
  } catch {
    // localStorage 可能已满，静默失败
    console.warn('Failed to cache favicon:', domain)
  }
}

/**
 * 多源降级获取 Favicon（带全局去重）
 *
 * 策略：
 * 1. 检查是否有正在进行的请求，如果有则复用
 * 2. Google Favicon API
 * 3. DuckDuckGo Favicon API
 * 4. 网站根目录 favicon.ico
 * 5. 返回 null（使用默认图标）
 *
 * @param domain - 域名
 * @returns 图标 URL 或 null
 */
export async function fetchFavicon(domain: string): Promise<string | null> {
  // 如果已经有正在进行的请求，直接返回该 Promise
  if (pendingRequests.has(domain)) {
    return pendingRequests.get(domain)!
  }

  // 创建新的请求 Promise
  const requestPromise = (async () => {
    const sources = [
      `https://www.google.com/s2/favicons?domain=${domain}&sz=64`,
      `https://icons.duckduckgo.com/ip3/${domain}.ico`,
      `https://${domain}/favicon.ico`,
    ]

    for (const source of sources) {
      try {
        const url = await fetchWithTimeout(source)
        // 验证图片是否有效
        const isValid = await validateImage(url)
        if (isValid) {
          return url
        }
      } catch {
        // 继续尝试下一个源
        continue
      }
    }

    return null
  })()

  // 缓存正在进行的请求
  pendingRequests.set(domain, requestPromise)

  try {
    const result = await requestPromise
    return result
  } finally {
    // 请求完成后从缓存中移除
    pendingRequests.delete(domain)
  }
}

/**
 * 带超时的 fetch 请求
 * @param url - 请求 URL
 * @returns 有效的图片 URL
 */
async function fetchWithTimeout(url: string): Promise<string> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), FAVICON_CACHE_CONFIG.REQUEST_TIMEOUT)

  try {
    const response = await fetch(url, {
      method: 'HEAD',
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    return url
  } catch (error) {
    clearTimeout(timeoutId)
    throw error
  }
}

/**
 * 验证图片 URL 是否有效
 * @param url - 图片 URL
 * @returns 是否有效
 */
function validateImage(url: string): Promise<boolean> {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      // 检查图片尺寸是否合理（避免返回 1x1 的占位图）
      const isValidSize = img.width >= 16 && img.height >= 16
      resolve(isValidSize)
    }
    img.onerror = () => resolve(false)
    img.src = url
  })
}

/**
 * 获取 Favicon（带缓存和请求去重）
 *
 * 优先从缓存读取，缓存未命中时异步获取并缓存。
 * 同一域名的请求会被去重，避免重复请求。
 *
 * @param url - 网站 URL
 * @param onSuccess - 获取成功回调
 * @param onError - 获取失败回调
 */
export function getFaviconWithCache(
  url: string,
  onSuccess?: (faviconUrl: string) => void,
  onError?: () => void
): string {
  const domain = getDomain(url)

  if (!domain) {
    onError?.()
    return ''
  }

  // 1. 尝试从缓存读取
  const cached = getCachedFavicon(domain)
  if (cached) {
    onSuccess?.(cached)
    return cached
  }

  // 2. 缓存未命中，异步获取（带全局去重）
  fetchFavicon(domain).then((faviconUrl) => {
    if (faviconUrl) {
      cacheFavicon(domain, faviconUrl)
      onSuccess?.(faviconUrl)
    } else {
      onError?.()
    }
  })

  // 3. 返回空字符串，等待异步加载
  return ''
}

/**
 * 清除指定域名的 Favicon 缓存
 * @param domain - 域名
 */
export function clearFaviconCache(domain: string): void {
  const cacheKey = `${FAVICON_CACHE_CONFIG.CACHE_KEY_PREFIX}${domain}`
  localStorage.removeItem(cacheKey)
}

/**
 * 清除所有 Favicon 缓存
 */
export function clearAllFaviconCache(): void {
  const keys = Object.keys(localStorage)
  keys.forEach((key) => {
    if (key.startsWith(FAVICON_CACHE_CONFIG.CACHE_KEY_PREFIX)) {
      localStorage.removeItem(key)
    }
  })
}
