import { useState, useEffect, useRef } from 'react'
import './App.css'
import teamLogo from './assets/ElectricBlue_logo.jpg'
import cloud_img from './assets/cloud_img.png'
import red_lightning from './assets/red_lightning.png'
import orange_lightning from './assets/orange_lightning.png'
import yellow_lightning from './assets/yellow_lightning.png'
import green_lightning from './assets/green_lightning.png'
import blue_lightning from './assets/blue_lightning.png'
import purple_lightning from './assets/purple_lightning.png'
import magenta_lightning from './assets/magenta_lightning.png'
import pink_lightning from './assets/pink_lightning.png'

function App() {
  const [count, setCount] = useState(0)
  const [message, setMessage] = useState('')
  const [chatLogs, setChatLogs] = useState([])
  const wsRef = useRef(null)
  const [currentBolt, setCurrentBolt] = useState(null)
  const timerRef = useRef(null)

  const boltColors = {
    red: red_lightning,
    orange: orange_lightning,
    yellow: yellow_lightning,
    green: green_lightning,
    blue: blue_lightning,
    purple: purple_lightning,
    magenta: magenta_lightning,
    pink: pink_lightning
  }

  // Initialize WebSocket connection
  useEffect(() => {
    // Connect to WebSocket server
    wsRef.current = new WebSocket('ws://localhost:8765')

    wsRef.current.onopen = () => {
      console.log('Connected to WebSocket server')
    }

    wsRef.current.onmessage = (event) => {
      const text = String(event.data).trim()
      console.log('Message from server:', text)

      let bolt = null
      let parsed = null
      try {
        parsed = JSON.parse(text)
        bolt = parsed.bolt ?? text
      } catch (err) {
        // Not JSON — treat raw text as bolt id
        bolt = text
      }

      if (bolt) triggerLightning(bolt)

      setChatLogs(prev => [...prev, {
        message: (parsed && parsed.original_message) || text,
        timestamp: (parsed && parsed.timestamp) || new Date().toISOString(),
        type: 'received'
      }])
    }

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    wsRef.current.onclose = () => {
      console.log('Disconnected from WebSocket server')
    }

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  const triggerLightning = (bolt) => {
    setCurrentBolt(bolt)
    if (timerRef.current) {
      clearTimeout(timerRef.current)
    }
    timerRef.current = setTimeout(() => {
      setCurrentBolt(null)
      timerRef.current = null
    }, 1000) // Show lightning for 1 second
  }

  // Send message on Enter key
  const handleKeyPress = (e) => {
    if (e.key !== 'Enter') return
    const bolt = message.trim().toLowerCase()
    if(!bolt) return
    
    //trigger bolt for testing
    if(boltColors[bolt]) triggerLightning(bolt)
      
    //forward to server
    if (wsRef.cirrent?.readyState === WebSocket.OPEN) {
      wsRef.current.send(message)
    }
      
    setMessage('')
    
  }

  return (
    <>
      <section>
        <p style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '10px' }}>
          Team Name: Electric Blue
        </p>
        <p style={{ fontSize: '18px', marginBottom: '20px' }}>
          Team Members: Leah Cheng, David Figueroa, Lila Forsythe, and Thai Phan
        </p>

        <img src={teamLogo} alt="Team Logo" style={{ width: '300px', height: 'auto', marginBottom: '-120px' , marginTop: '-20px'}} />
      </section>
      <section className="cloud-section">
            <img src={cloud_img} alt="Cloud" style={{ width: '1000px', height: 'auto', marginBottom: '-132px' }} />
      </section>
      <section className="lightning-row">
        {Object.entries(boltColors).map(([id, src]) => (
          <img
          key ={id}
          src={src}
          alt={id}
          className={'bolt ' + (currentBolt === id ? 'active' : '')}
          />
        ))}

      </section>
  
      <section id="center">

        {/* WebSocket Message Input */}
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type message and press Enter to send"
          style={{
            marginTop: '20px',
            padding: '10px',
            borderRadius: '4px',
            border: '1px solid #ccc',
            width: '300px',
            fontSize: '16px'
          }}
        />
      </section>
    </>
  )
}

export default App
