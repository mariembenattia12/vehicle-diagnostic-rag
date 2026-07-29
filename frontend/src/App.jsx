import { useState, useRef, useEffect } from 'react'
import './App.css'

const API_URL = import.meta.env.DEV ? 'http://127.0.0.1:8000' : ''

const EXAMPLE_QUESTIONS = [
  "Qu'est-ce que le code P0171 ?",
  "Rappels connus sur la Honda Civic ?",
  "Symptômes d'un problème de transmission",
]

function highlightCodes(text) {
  const regex = /\b([PBCU][0-9]{4})\b/g
  const parts = []
  let lastIndex = 0
  let match
  let key = 0

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index))
    }
    parts.push(
      <span className="dtc-chip" key={`chip-${key++}`}>{match[0]}</span>
    )
    lastIndex = match.index + match[0].length
  }
  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex))
  }
  return parts
}

function formatTime(date) {
  return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [connection, setConnection] = useState('checking') // checking | online | offline
  const [copiedIndex, setCopiedIndex] = useState(null)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)
  const [recording, setRecording] = useState(false)
  const [transcribing, setTranscribing] = useState(false)
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])

  useEffect(() => {
    checkHealth()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_URL}/health`)
      setConnection(res.ok ? 'online' : 'offline')
    } catch {
      setConnection('offline')
    }
  }

  const autoResize = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 140) + 'px'
  }

  const handleInputChange = (e) => {
    setInput(e.target.value)
    autoResize()
  }

  const sendMessage = async (overrideText) => {
    const question = (overrideText ?? input).trim()
    if (!question || loading) return

    setMessages(prev => [...prev, {
      role: 'user',
      content: question,
      timestamp: new Date(),
    }])
    setInput('')
    setLoading(true)
    requestAnimationFrame(autoResize)

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, session_id: sessionId }),
      })

     if (!response.ok) {
        let detail = `Erreur serveur (${response.status})`
        try {
          const errBody = await response.json()
          if (errBody.detail) detail = errBody.detail
        } catch {}
        throw new Error(detail)
      }

      const data = await response.json()
      setSessionId(data.session_id)
      setConnection('online')
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sourcesCount: data.sources_count,
        timestamp: new Date(),
      }])
    } catch (error) {
      setConnection('offline')
      setMessages(prev => [...prev, {
        role: 'error',
        content: `${error.message} — vérifie que le serveur FastAPI tourne sur le port 8000.`,
        timestamp: new Date(),
      }])
    } finally {
      setLoading(false)
    }
  }
const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      chunksRef.current = []

      recorder.ondataavailable = (e) => chunksRef.current.push(e.data)
      recorder.onstop = async () => {
        stream.getTracks().forEach(track => track.stop())
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setTranscribing(true)

        const formData = new FormData()
        formData.append('audio', audioBlob, 'recording.webm')

        try {
          const res = await fetch(`${API_URL}/transcribe`, {
            method: 'POST',
            body: formData,
          })
          const data = await res.json()
          setInput(prev => (prev ? prev + ' ' : '') + data.text)
          requestAnimationFrame(autoResize)
        } catch {
          setMessages(prev => [...prev, {
            role: 'error',
            content: 'Erreur de transcription audio.',
            timestamp: new Date(),
          }])
        } finally {
          setTranscribing(false)
        }
      }

      recorder.start()
      mediaRecorderRef.current = recorder
      setRecording(true)
    } catch {
      setMessages(prev => [...prev, {
        role: 'error',
        content: "Impossible d'accéder au microphone.",
        timestamp: new Date(),
      }])
    }
  }

  const stopRecording = () => {
    mediaRecorderRef.current?.stop()
    setRecording(false)
  }
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleCopy = (text, index) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 1500)
  }

  const handleClear = () => {
    setMessages([])
    setSessionId(null)
  }

  const statusLabel = {
    checking: 'Vérification…',
    online: 'Connecté',
    offline: 'Hors ligne',
  }[connection]

  return (
    <div className="app">
      <header className="header">
        <div className="header-top">
          <div>
            <span className="eyebrow">ASSISTANT IA · OBD-II</span>
            <h1>Diagnostic véhicule</h1>
          </div>
          <button className="icon-btn" onClick={handleClear} aria-label="Nouvelle conversation" title="Nouvelle conversation">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 12a9 9 0 1 0 3-6.7" />
              <path d="M3 4v5h5" />
            </svg>
          </button>
        </div>
        <div className="status-row">
          <span className={`status-dot ${connection}`} />
          <span className="status-label">{statusLabel}</span>
          <span className="status-sep">·</span>
          <span className="status-label">Codes DTC · Plaintes NHTSA · Rappels</span>
        </div>
      </header>

      <div className="chat-window">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>Décris un symptôme ou demande un code défaut.</p>
            <div className="example-chips">
              {EXAMPLE_QUESTIONS.map((q, i) => (
                <button key={i} className="example-chip" onClick={() => sendMessage(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="bubble">
              <div className="bubble-text">{highlightCodes(msg.content)}</div>
              <div className="bubble-footer">
                <span className="timestamp">{formatTime(msg.timestamp)}</span>
                {msg.sourcesCount !== undefined && (
                  <span className="sources-count">{msg.sourcesCount} source(s)</span>
                )}
                {msg.role === 'assistant' && (
                  <button
                    className="copy-btn"
                    onClick={() => handleCopy(msg.content, i)}
                    aria-label="Copier la réponse"
                    title="Copier la réponse"
                  >
                    {copiedIndex === i ? (
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M20 6 9 17l-5-5" />
                      </svg>
                    ) : (
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" />
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                      </svg>
                    )}
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="bubble">
              <div className="loading-row">
                <span className="loading-label">Analyse en cours</span>
                <span className="dots">
                  <span></span><span></span><span></span>
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-bar">
        <button
          className={`mic-btn ${recording ? 'recording' : ''}`}
          onClick={recording ? stopRecording : startRecording}
          disabled={transcribing}
          aria-label={recording ? "Arrêter l'enregistrement" : "Enregistrer une question"}
          title={recording ? "Arrêter l'enregistrement" : "Enregistrer une question"}
        >
          {transcribing ? (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" className="mic-spin">
              <path d="M21 12a9 9 0 1 1-6.219-8.56" strokeLinecap="round" />
            </svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="9" y="2" width="6" height="12" rx="3" fill="currentColor" stroke="none" />
              <path d="M5 10v1a7 7 0 0 0 14 0v-1" />
              <path d="M12 18v3" />
              <path d="M9 21h6" />
            </svg>
          )}
        </button>
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Écris ta question ici…"
          rows={1}
        />
        <button onClick={() => sendMessage()} disabled={loading || !input.trim()}>
          Envoyer
        </button>
      </div>
    </div>
  )
}

export default App