import { useState, useEffect, useRef } from 'react'
import './App.css'
import teamLogo from './assets/ElectricBlue_logo.jpg'
import teamPhoto from './assets/band-photo.png'
import cloud_img from './assets/cloud_img.png'
import red_lightning from './assets/red_lightning.png'
import orange_lightning from './assets/orange_lightning.png'
import yellow_lightning from './assets/yellow_lightning.png'
import green_lightning from './assets/green_lightning.png'
import blue_lightning from './assets/blue_lightning.png'
import purple_lightning from './assets/purple_lightning.png'
import magenta_lightning from './assets/magenta_lightning.png'
import pink_lightning from './assets/pink_lightning.png'
import teamVideo from './assets/team 10.mp4'
import Octave from './assets/Octave for stormcaster.mp3'
import Vibrato from './assets/Vibrato.mp3'
import Retro from './assets/Retro.mp3'
import Bubbles from './assets/Bubbles.mp3'
import Volume from './assets/Volume control.mp3'


function App() {
  const [count, setCount] = useState(0)
  const [message, setMessage] = useState('')
  const [chatLogs, setChatLogs] = useState([])
  const wsRef = useRef(null)
  const videoRef = useRef(null)
  const [currentBolt, setCurrentBolt] = useState(null)
  const timerRef = useRef(null)

  useEffect(() => {
    console.log('videoRef on mount', videoRef.current)
  }, [])

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

  const audioRefs = {
    Octave: useRef(null),
    Vibrato: useRef(null),
    Retro: useRef(null),
    Bubbles: useRef(null),
    Volume: useRef(null)  
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

      console.log('Attempting to parse incoming message')

      let bolt = null
      let parsed = null
      try {
        parsed = JSON.parse(text)
        bolt = parsed.bolt ?? parsed.original_message ?? text
      } catch (err) {
        // Not JSON — treat raw text as bolt id
        bolt = text
      }

      console.log('After parse, bolt candidate:', bolt, 'parsed:', parsed)

      if (typeof bolt === 'string') {
        bolt = bolt.toLowerCase()
      }

      if (!boltColors[bolt] && typeof bolt === 'string') {
        const found = bolt.match(/\b(red|orange|yellow|green|blue|purple|magenta|pink)\b/i)
        if (found) {
          bolt = found[1].toLowerCase()
        }
      }

      console.log('Final bolt chosen after regex check:', bolt)

      if (boltColors[bolt]) {
        triggerLightning(bolt)
      } else {
        console.warn('Unknown bolt color from server:', bolt)
      }

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
    console.log('TriggerLightning called with:', bolt)
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
    if (!bolt) return

    // trigger bolt for testing
    if (boltColors[bolt]) triggerLightning(bolt)
    else console.warn('Unknown test bolt color:', bolt)

    // forward to server
    if (wsRef.current?.readyState === WebSocket.OPEN) {
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
        <p style={{ fontSize: '18px' , marginBottom: '-40px'}}>
          Instrument name: STORMCASTER
        </p>
        <p style={{ fontSize: '16px', margin: '50px'}}>
          Description: Our theme is weather based as our name is Electric Blue so our instrument shape took inspiration from that.
          Our instrument is a cloud with playable drops for each note. Each drop triggers a light on the cloud. 
        </p>
        <p>
          Setlist: Twinkle Twinkle Little Star, Happy Birthday
        </p>
        <p style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '10px' }}>
          Bolts:
        </p>
        <div className="bolt-info-grid">
          <div className="bolt-info-cell bolt-red">
            <div className="bolt-info-color">Red</div>
            <div className="bolt-info-note">C4: 261.63</div>
          </div>
          <div className="bolt-info-cell bolt-orange">
            <div className="bolt-info-color">Orange</div>
            <div className="bolt-info-note">D4: 293.66</div>
          </div>
          <div className="bolt-info-cell bolt-yellow">
            <div className="bolt-info-color">Yellow</div>
            <div className="bolt-info-note">E4: 329.63</div>
          </div>
          <div className="bolt-info-cell bolt-green">
            <div className="bolt-info-color">Green</div>
            <div className="bolt-info-note">F4: 349.23</div>
          </div>
          <div className="bolt-info-cell bolt-blue">
            <div className="bolt-info-color">Blue</div>
            <div className="bolt-info-note">G4: 392.00</div>
          </div>
          <div className="bolt-info-cell bolt-purple">
            <div className="bolt-info-color">Purple</div>
            <div className="bolt-info-note">A4: 440.00</div>
          </div>
          <div className="bolt-info-cell bolt-magenta">
            <div className="bolt-info-color">Magenta</div>
            <div className="bolt-info-note">B4: 493.88</div>
          </div>
          <div className="bolt-info-cell bolt-pink">
            <div className="bolt-info-color">Pink</div>
            <div className="bolt-info-note">C5: 523.25</div>
          </div>
        </div>

      <p style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '10px' }}>
          Sounds:
        </p>
        <div className="sound-info-grid">
          <div className="member-info-cell">
            <div className="member-info-name">Octave</div>
            <div className="member-info-desc">
              <audio ref={audioRefs.Octave} src={Octave} />
              <button onClick={() => audioRefs.Octave.current.play()}>play</button>
            </div>
          </div>
          <div className="member-info-cell">
            <div className="member-info-name">Vibrato</div>
            <div className="member-info-desc">
              <audio ref={audioRefs.Vibrato} src={Vibrato} />
              <button onClick={() => audioRefs.Vibrato.current.play()}>play</button>
            </div>
          </div>
          <div className="member-info-cell">
            <div className="member-info-name">Retro</div>
            <div className="member-info-desc">
              <audio ref={audioRefs.Retro} src={Retro} />
              <button onClick={() => audioRefs.Retro.current.play()}>play</button>
            </div>
          </div>
          <div className="member-info-cell">
            <div className="member-info-name">Bubbles</div>
            <div className="member-info-desc">
              <audio ref={audioRefs.Bubbles} src={Bubbles} />
              <button onClick={() => audioRefs.Bubbles.current.play()}>play</button>
            </div>
          </div>
          <div className="member-info-cell">
            <div className="member-info-name">Volume Control</div>
            <div className="member-info-desc">
              <audio ref={audioRefs.Volume} src={Volume} />
              <button onClick={() => audioRefs.Volume.current.play()}>play</button>
            </div>
          </div>
        </div>

        <p style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '10px' }}>
          Members:
        </p>
        <div className="member-info-grid">
          <div className="member-info-cell">
            <div className="member-info-name">Leah Cheng</div>
            <div className="member-info-desc">Major: Mechanical Engineering | Worked on some of the CAD, did the soldering for the buttons painted the cloud, and is our main performer.</div>
          </div>
          <div className="member-info-cell">
            <div className="member-info-name">Lila Forsythe</div>
            <div className="member-info-desc">Major: Computer Science | Worked on some of the CAD, came up with the design and theme for the instrument, made the website and the visual aspect.</div>
          </div>
          <div className="member-info-cell">
            <div className="member-info-name">David Figueroa</div>
            <div className="member-info-desc">Major: Electrical Engineering | Worked on the circuits and the communication between the microcontroller and the hardware. Figured out how the audio output works.</div>
          </div>
          <div className="member-info-cell">
            <div className="member-info-name">Thai Phan</div>
            <div className="member-info-desc">Major: Mechanical Engineering | Worked on some aspects of the website</div>
          </div>
        </div>
        <img src={teamLogo} alt="Team Logo" style={{ width: '300px', height: 'auto', marginBottom: '-50px'}} />
        <img src={teamPhoto} alt="Team Photo" style={{ width: '300px', height: 'auto', marginBottom: '-50px'}} />
        <section className="video-section">
          <h2>Performance Video</h2>
          <video
            ref={videoRef}
            controls
            width="640"
            preload="metadata"
            muted={false}
            onLoadedMetadata={() => {
              console.log('Video duration', videoRef.current?.duration)
              console.log('Audio track count', videoRef.current?.audioTracks?.length)
              console.log('videoRef muted', videoRef.current?.muted)
              console.log('videoRef volume', videoRef.current?.volume)
            }}
            onPlay={() => console.log('video onPlay', { muted: videoRef.current?.muted, volume: videoRef.current?.volume })}
            onPause={() => console.log('video onPause')}
            onError={(e) => console.error('Video playback error', e)}
          >
            <source src={teamVideo} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          <div style={{ marginTop: '12px' }}>
            <button onClick={() => videoRef.current?.play()}>Play</button>
            <button onClick={() => videoRef.current?.pause()}>Pause</button>
            <button onClick={() => {
              if (videoRef.current) {
                videoRef.current.muted = false
                videoRef.current.volume = 1
                console.log('Unmuted video; volume set to', videoRef.current.volume)
              }
            }}>
              Unmute
            </button>
          </div>
        </section>
      </section>
      <section className="cloud-section">
            <img src={cloud_img} alt="Cloud" style={{ width: '1000px', height: 'auto', marginBottom: '-132px'}} />
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
