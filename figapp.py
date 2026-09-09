import { useState, useEffect, useRef } from 'react';
import { AlertCircle, Camera, Eye } from 'lucide-react';
import { IntegrityViolation } from '../utils/integrityScoring';
import { toast } from 'sonner';

interface IntegrityMonitorProps {
  isActive: boolean;
  onViolation: (violation: IntegrityViolation) => void;
}

export function IntegrityMonitor({ isActive, onViolation }: IntegrityMonitorProps) {
  const [faceDetected, setFaceDetected] = useState(false);
  const [monitoringStatus, setMonitoringStatus] = useState<'active' | 'warning' | 'error' | 'disabled'>('disabled');
  const [webcamEnabled, setWebcamEnabled] = useState(false);
  const [showRequestButton, setShowRequestButton] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const previewVideoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const detectionIntervalRef = useRef<number>();
  const awayTimeRef = useRef(0);
  const lastFaceTimeRef = useRef(Date.now());

  // Request webcam access
  const requestWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });
      
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      if (previewVideoRef.current) {
        previewVideoRef.current.srcObject = stream;
      }
      setWebcamEnabled(true);
      setMonitoringStatus('active');
      setShowRequestButton(false);
    } catch (error) {
      console.log('Webcam access denied:', error);
      setWebcamEnabled(false);
      setMonitoringStatus('disabled');
      setShowRequestButton(true);
      toast.info('Webcam monitoring disabled - interview will continue with reduced integrity monitoring');
    }
  };

  useEffect(() => {
    if (!isActive) return;

    requestWebcam();

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [isActive]);

  // Simple face detection (checks for video data changes)
  useEffect(() => {
    if (!isActive || !webcamEnabled || !videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let lastImageData: ImageData | null = null;

    detectionIntervalRef.current = window.setInterval(() => {
      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        
        // Simple motion detection - if pixels change significantly, face is present
        if (lastImageData) {
          let diff = 0;
          for (let i = 0; i < imageData.data.length; i += 4) {
            diff += Math.abs(imageData.data[i] - lastImageData.data[i]);
          }
          
          const changePercentage = diff / (imageData.data.length / 4) / 255 * 100;
          
          if (hasFace) {
            setFaceDetected(true);
            setMonitoringStatus('active');
            lastFaceTimeRef.current = Date.now();
          } else {
            const awayDuration = (Date.now() - lastFaceTimeRef.current) / 1000;
            
            if (awayDuration > 3) {
              setFaceDetected(false);
              setMonitoringStatus('warning');
              
              if (awayDuration > 5 && Math.floor(awayDuration) % 5 === 0) {
                toast.warning('Face not detected. Please stay visible.');
                onViolation({
                  type: 'face_missing',
                  timestamp: Date.now(),
                  duration: awayDuration
                });
              }
            }
          }
        }
        
        lastImageData = imageData;
      }
    }, 1000); // Check every second

    return () => {
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current);
      }
    };
  }, [isActive, webcamEnabled, onViolation]);

  // Tab/Focus monitoring
  useEffect(() => {
    if (!isActive) return;

    let blurStartTime: number | null = null;

    const handleVisibilityChange = () => {
      if (document.hidden) {
        blurStartTime = Date.now();
        toast.warning('Tab switch detected!');
        onViolation({
          type: 'tab_switch',
          timestamp: Date.now()
        });
      } else if (blurStartTime) {
        const duration = (Date.now() - blurStartTime) / 1000;
        awayTimeRef.current += duration;
        blurStartTime = null;
      }
    };

    const handleWindowBlur = () => {
      blurStartTime = Date.now();
      toast.warning('Window focus lost!');
      onViolation({
        type: 'blur',
        timestamp: Date.now()
      });
    };

    const handleWindowFocus = () => {
      if (blurStartTime) {
        const duration = (Date.now() - blurStartTime) / 1000;
        awayTimeRef.current += duration;
        blurStartTime = null;
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleWindowBlur);
    window.addEventListener('focus', handleWindowFocus);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleWindowBlur);
      window.removeEventListener('focus', handleWindowFocus);
    };
  }, [isActive, onViolation]);

  // Fullscreen monitoring
  useEffect(() => {
    if (!isActive) return;

    const handleFullscreenChange = () => {
      if (!document.fullscreenElement) {
        toast.error('Fullscreen exited! Please return to fullscreen.');
        onViolation({
          type: 'fullscreen_exit',
          timestamp: Date.now()
        });
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);

    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, [isActive, onViolation]);

  if (!isActive) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {/* Status Indicator */}
      <div className={`px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 ${
        monitoringStatus === 'active' ? 'bg-green-600' :
        monitoringStatus === 'warning' ? 'bg-yellow-600' :
        monitoringStatus === 'disabled' ? 'bg-gray-600' :
        'bg-red-600'
      }`}>
        <Camera className="w-5 h-5 text-white" />
        <span className="text-white text-sm font-medium">
          {monitoringStatus === 'active' ? 'Monitoring Active' :
           monitoringStatus === 'warning' ? 'Face Not Detected' :
           monitoringStatus === 'disabled' ? 'Webcam Disabled' :
           'Camera Error'}
        </span>
        {faceDetected && (
          <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
        )}
      </div>

      {/* Hidden video and canvas for face detection */}
      <div className="hidden">
        <video ref={videoRef} autoPlay playsInline muted />
        <canvas ref={canvasRef} />
      </div>

      {/* Webcam Preview (small) */}
      {streamRef.current && (
        <div className="relative w-48 h-36 rounded-lg overflow-hidden shadow-lg border-2 border-white">
          <video
            ref={previewVideoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />
          {faceDetected && (
            <div className="absolute top-2 left-2 bg-green-600 text-white px-2 py-1 rounded text-xs flex items-center gap-1">
              <Eye className="w-3 h-3" />
              Face Detected
            </div>
          )}
          {!faceDetected && (
            <div className="absolute top-2 left-2 bg-red-600 text-white px-2 py-1 rounded text-xs flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              No Face
            </div>
          )}
        </div>
      )}
    </div>
  );
}
