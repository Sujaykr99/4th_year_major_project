import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

const ArcReactor = ({ onComplete }) => {
  const [progress, setProgress] = useState(0)
  const [textStage, setTextStage] = useState(0)

  const texts = [
    "INITIALIZING NEURAL PATHWAYS...",
    "PROCESSING GITHUB NODES...",
    "COMPILING READINESS SCORE...",
    "ALIGNING CAREER VECTORS...",
    "SYSTEM READY."
  ]

  useEffect(() => {
    // Simulate loading progress
    const duration = 4000 // 4 seconds total
    const intervalTime = 50
    const steps = duration / intervalTime

    let currentStep = 0
    const timer = setInterval(() => {
      currentStep++
      const newProgress = Math.min(Math.round((currentStep / steps) * 100), 100)
      setProgress(newProgress)
      
      // Update text based on progress
      if (newProgress > 80) setTextStage(4)
      else if (newProgress > 60) setTextStage(3)
      else if (newProgress > 40) setTextStage(2)
      else if (newProgress > 20) setTextStage(1)

      if (currentStep >= steps) {
        clearInterval(timer)
        setTimeout(() => {
          if (onComplete) onComplete()
        }, 500)
      }
    }, intervalTime)

    return () => clearInterval(timer)
  }, [onComplete])

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] w-full">
      <div className="relative w-64 h-64 flex items-center justify-center">
        {/* Outer Ring (Slow, Counter-Clockwise) */}
        <motion.div
          className="absolute inset-0 rounded-full border-[1px] border-[#1f7134] opacity-40"
          animate={{ rotate: -360 }}
          transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
          style={{ borderStyle: 'dashed' }}
        />
        
        {/* Middle Ring (Medium, Clockwise) */}
        <motion.div
          className="absolute inset-[15px] rounded-full border-2 border-[#49ef83] opacity-60"
          animate={{ rotate: 360 }}
          transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
          style={{ borderTopColor: 'transparent', borderBottomColor: 'transparent' }}
        />
        
        {/* Inner Ring (Fast, Counter-Clockwise) */}
        <motion.div
          className="absolute inset-[30px] rounded-full border-[3px] border-[#a0f5b9] opacity-80"
          animate={{ rotate: -360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          style={{ borderLeftColor: 'transparent', borderRightColor: 'transparent' }}
        />

        {/* Pulse Core */}
        <motion.div
          className="absolute inset-[45px] rounded-full bg-[#49ef83]"
          animate={{ 
            boxShadow: [
              "0 0 20px rgba(73,239,131,0.2)",
              "0 0 60px rgba(73,239,131,0.6)",
              "0 0 20px rgba(73,239,131,0.2)"
            ]
          }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          style={{ opacity: 0.15 }}
        />

        {/* Percentage Text */}
        <div className="absolute z-10 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold font-[var(--mono)] text-[#a0f5b9] drop-shadow-[0_0_10px_rgba(160,245,185,0.8)]">
            {progress}%
          </span>
          <span className="text-[10px] text-[#49ef83] mt-1 font-[var(--mono)] tracking-[0.2em]">
            PROCESSING
          </span>
        </div>
      </div>

      {/* Terminal Text Output */}
      <div className="mt-12 h-10 flex items-center justify-center">
        <motion.p
          key={textStage}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="font-[var(--mono)] text-xs text-[#75df8e] tracking-widest text-center"
        >
          {`> ${texts[textStage]}`}
          <motion.span 
            animate={{ opacity: [1, 0] }} 
            transition={{ duration: 0.8, repeat: Infinity }}
            className="ml-1 inline-block w-2 h-3 bg-[#49ef83]"
          />
        </motion.p>
      </div>
    </div>
  )
}

export default ArcReactor
