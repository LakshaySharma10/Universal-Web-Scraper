import { useState } from 'react'

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [expandedSections, setExpandedSections] = useState(new Set())

  const handleScrape = async () => {
    if (!url.trim()) {
      setError('Please enter a URL')
      return
    }

    try {
      new URL(url)
    } catch {
      setError('Please enter a valid URL (must start with http:// or https://)')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Scraping failed')
      }

      const data = await response.json()
      setResult(data.result)
    } catch (err) {
      setError(err.message || 'An error occurred while scraping')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    if (!result) return

    const dataStr = JSON.stringify({ result }, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `scrape-result-${Date.now()}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const toggleSection = (sectionId) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId)
    } else {
      newExpanded.add(sectionId)
    }
    setExpandedSections(newExpanded)
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <header className="bg-black border-b border-gray-800 py-6 px-4">
        <div className="max-w-7xl flex justify-center r mx-auto">
          <h1 className="text-3xl font-bold text-white mb-2">Universal Website Scraper</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 w-full">
        <div className="bg-gray-900 rounded-lg p-6 mb-6 border border-gray-800">
          <div className="flex flex-col sm:flex-row gap-4">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={loading}
              onKeyPress={(e) => e.key === 'Enter' && !loading && handleScrape()}
            />
            <button
              onClick={handleScrape}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors duration-200"
            >
              {loading ? 'Scraping...' : 'Scrape'}
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-900/50 border border-red-800 text-red-200 px-4 py-3 rounded-lg mb-6">
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
              <h2 className="text-2xl font-bold text-white">Scraping Results</h2>
              <button 
                onClick={handleDownload} 
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors duration-200"
              >
                Download JSON
              </button>
            </div>

            <div className="bg-gray-800 rounded-lg p-4 mb-6 border border-gray-700">
              <h3 className="text-xl font-semibold text-white mb-4">Page Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div><strong className="text-gray-400">URL:</strong> <span className="text-white break-all">{result.url}</span></div>
                <div><strong className="text-gray-400">Title:</strong> <span className="text-white">{result.meta.title || 'N/A'}</span></div>
                <div><strong className="text-gray-400">Description:</strong> <span className="text-white">{result.meta.description || 'N/A'}</span></div>
                <div><strong className="text-gray-400">Language:</strong> <span className="text-white">{result.meta.language}</span></div>
                <div className="md:col-span-2"><strong className="text-gray-400">Scraped At:</strong> <span className="text-white">{new Date(result.scrapedAt).toLocaleString()}</span></div>
              </div>
            </div>

            {result.interactions && (
              <div className="bg-gray-800 rounded-lg p-4 mb-6 border border-gray-700">
                <h3 className="text-xl font-semibold text-white mb-4">Interactions</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div><strong className="text-gray-400">Clicks:</strong> <span className="text-white">{result.interactions.clicks.length}</span></div>
                  <div><strong className="text-gray-400">Scrolls:</strong> <span className="text-white">{result.interactions.scrolls}</span></div>
                  <div><strong className="text-gray-400">Pages Visited:</strong> <span className="text-white">{result.interactions.pages.length}</span></div>
                </div>
                {result.interactions.clicks.length > 0 && (
                  <div>
                    <strong className="text-gray-400">Click Selectors:</strong>
                    <ul className="list-disc list-inside mt-2 space-y-1 text-gray-300">
                      {result.interactions.clicks.map((click, idx) => (
                        <li key={idx} className="text-sm">{click}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {result.errors && result.errors.length > 0 && (
              <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 mb-6">
                <h3 className="text-xl font-semibold text-red-300 mb-2">Errors</h3>
                <ul className="list-disc list-inside space-y-1 text-red-200">
                  {result.errors.map((err, idx) => (
                    <li key={idx} className="text-sm">
                      <strong>{err.phase}:</strong> {err.message}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div>
              <h3 className="text-2xl font-bold text-white mb-4">Sections ({result.sections.length})</h3>
              <div className="space-y-4">
                {result.sections.map((section) => (
                  <div key={section.id} className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                    <div
                      className="p-4 cursor-pointer hover:bg-gray-750 flex justify-between items-center transition-colors"
                      onClick={() => toggleSection(section.id)}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                        <span className="px-2 py-1 bg-blue-600 text-white text-xs font-semibold rounded uppercase">
                          {section.type}
                        </span>
                        <span className="font-semibold text-white">{section.label}</span>
                      </div>
                      <span className="text-gray-400">
                        {expandedSections.has(section.id) ? '▼' : '▶'}
                      </span>
                    </div>

                    {expandedSections.has(section.id) && (
                      <div className="p-6 bg-gray-900 border-t border-gray-700 space-y-4">
                        <div className="space-y-4">
                          <div>
                            <strong className="text-gray-400">ID:</strong>
                            <span className="text-white ml-2">{section.id}</span>
                          </div>
                          <div>
                            <strong className="text-gray-400">Source URL:</strong>
                            <span className="text-white ml-2 break-all">{section.sourceUrl}</span>
                          </div>
                          <div>
                            <strong className="text-gray-400">Truncated:</strong>
                            <span className="text-white ml-2">{section.truncated ? 'Yes' : 'No'}</span>
                          </div>

                          {section.content.headings.length > 0 && (
                            <div>
                              <strong className="text-gray-400">Headings:</strong>
                              <ul className="list-disc list-inside mt-2 space-y-1 text-gray-300">
                                {section.content.headings.map((heading, idx) => (
                                  <li key={idx}>{heading}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {section.content.text && (
                            <div>
                              <strong className="text-gray-400">Text:</strong>
                              <p className="text-gray-300 mt-2 leading-relaxed max-h-48 overflow-y-auto">{section.content.text}</p>
                            </div>
                          )}

                          {section.content.links.length > 0 && (
                            <div>
                              <strong className="text-gray-400">Links ({section.content.links.length}):</strong>
                              <ul className="list-disc list-inside mt-2 space-y-1">
                                {section.content.links.slice(0, 10).map((link, idx) => (
                                  <li key={idx}>
                                    <a href={link.href} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 hover:underline break-all">
                                      {link.text || link.href}
                                    </a>
                                  </li>
                                ))}
                                {section.content.links.length > 10 && (
                                  <li className="text-gray-500">... and {section.content.links.length - 10} more</li>
                                )}
                              </ul>
                            </div>
                          )}

                          {section.content.images.length > 0 && (
                            <div>
                              <strong className="text-gray-400">Images ({section.content.images.length}):</strong>
                              <ul className="list-disc list-inside mt-2 space-y-1">
                                {section.content.images.slice(0, 5).map((img, idx) => (
                                  <li key={idx}>
                                    <a href={img.src} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 hover:underline break-all">
                                      {img.alt || img.src}
                                    </a>
                                  </li>
                                ))}
                                {section.content.images.length > 5 && (
                                  <li className="text-gray-500">... and {section.content.images.length - 5} more</li>
                                )}
                              </ul>
                            </div>
                          )}

                          {section.content.lists.length > 0 && (
                            <div>
                              <strong className="text-gray-400">Lists ({section.content.lists.length}):</strong>
                              {section.content.lists.map((list, listIdx) => (
                                <ul key={listIdx} className="list-disc list-inside mt-2 space-y-1 text-gray-300">
                                  {list.map((item, itemIdx) => (
                                    <li key={itemIdx}>{item}</li>
                                  ))}
                                </ul>
                              ))}
                            </div>
                          )}

                          {section.content.tables.length > 0 && (
                            <div>
                              <strong className="text-gray-400">Tables ({section.content.tables.length}):</strong>
                              {section.content.tables.map((table, tableIdx) => (
                                <div key={tableIdx} className="mt-2 overflow-x-auto">
                                  {table.rows && table.rows.length > 0 && (
                                    <table className="min-w-full border border-gray-700">
                                      <tbody>
                                        {table.rows.slice(0, 5).map((row, rowIdx) => (
                                          <tr key={rowIdx} className="border-b border-gray-700">
                                            {row.map((cell, cellIdx) => (
                                              <td key={cellIdx} className="px-4 py-2 text-gray-300 border-r border-gray-700 last:border-r-0">{cell}</td>
                                            ))}
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  )}
                                  {table.rows && table.rows.length > 5 && (
                                    <p className="text-gray-500 mt-2">... and {table.rows.length - 5} more rows</p>
                                  )}
                                </div>
                              ))}
                            </div>
                          )}

                          <div>
                            <strong className="text-gray-400">Raw HTML:</strong>
                            <pre className="bg-gray-950 p-4 rounded mt-2 overflow-x-auto text-xs text-gray-400 max-h-64 overflow-y-auto">
                              {section.rawHtml.substring(0, 1000)}
                              {section.rawHtml.length > 1000 && '...'}
                            </pre>
                          </div>

                          <div>
                            <strong className="text-gray-400">Full JSON:</strong>
                            <pre className="bg-gray-950 p-4 rounded mt-2 overflow-x-auto text-xs text-gray-400 max-h-64 overflow-y-auto">
                              {JSON.stringify(section, null, 2)}
                            </pre>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
