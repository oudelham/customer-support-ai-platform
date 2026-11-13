import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { HelpCircle, Mic, Send, Turtle, Volume2, XCircle } from 'lucide-react';
import { apiFetch } from '../api/client';

type MicState = 'idle' | 'recording' | 'processing' | 'speaking';

interface Correction {
  original: string;
  corrected: string;
  reason: string;
  error_type: string;
  native_explanation?: string | null;
}

interface ChatItem {
  role: 'user' | 'tutor';
  text: string;
  correction?: Correction | null;
  audioBase64?: string | null;
}

function getSupportedMimeType(): string {
  if (typeof MediaRecorder === 'undefined') return '';
  if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) return 'audio/webm;codecs=opus';
  if (MediaRecorder.isTypeSupported('audio/mp4')) return 'audio/mp4';
  return '';
}

export default function SessionPage() {
  const { id: sessionId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [messages, setMessages] = useState<ChatItem[]>([]);
  const [micState, setMicState] = useState<MicState>('idle');
  const [textInput, setTextInput] = useState('');
  const [samples, setSamples] = useState<string[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [hasConsent, setHasConsent] = useState<boolean>(
    () => localStorage.getItem('Lingo2U_mic_consent') === 'true'
  );
  const [showConsentModal, setShowConsentModal] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const playBase64Audio = (base64: string) => {
    if (!base64) return;
    setMicState('speaking');
    const audio = new Audio(`data:audio/mp3;base64,${base64}`);
    audio.onended = () => setMicState('idle');
    audio.onerror = () => setMicState('idle');
    audio.play().catch(() => setMicState('idle'));
  };

  useEffect(() => {
    apiFetch(`/sessions/${sessionId}`).then((data) => {
      setMessages(
        data.messages.map((m: any) => ({
          role: m.role,
          text: m.content,
          correction: m.correction,
        }))
      );
    });
  }, [sessionId]);

  const startRecording = async () => {
    if (!hasConsent) {
      setShowConsentModal(true);
      return;
    }
    setErrorMsg(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = getSupportedMimeType();
      const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);

      chunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: mimeType || 'audio/webm' });
        await uploadVoiceTurn(blob, mimeType.includes('mp4') ? 'turn.mp4' : 'turn.webm');
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setMicState('recording');
    } catch {
      setErrorMsg(
        'Microphone access is blocked. Please allow microphone access in your browser, or type below.'
      );
      setMicState('idle');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      setMicState('processing');
      mediaRecorderRef.current.stop();
    }
  };

  const uploadVoiceTurn = async (blob: Blob, filename: string) => {
    try {
      const formData = new FormData();
      formData.append('audio', blob, filename);

      const res = await apiFetch(`/sessions/${sessionId}/voice`, {
        method: 'POST',
        body: formData,
        headers: { 'X-Idempotency-Key': crypto.randomUUID() },
      });

      if (res.transcript) {
        setMessages((prev) => [
          ...prev,
          { role: 'user', text: res.transcript, correction: res.correction },
          { role: 'tutor', text: res.tutor_text, audioBase64: res.audio_base64 },
        ]);
        if (res.audio_base64) playBase64Audio(res.audio_base64);
        else setMicState('idle');
      } else {
        setErrorMsg(res.tutor_text);
        setMicState('idle');
      }
    } catch {
      setErrorMsg('Connection interrupted. Please try sending your reply again.');
      setMicState('idle');
    }
  };

  const handleTextSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!textInput.trim() || micState === 'processing') return;
    const text = textInput.trim();
    setTextInput('');
    setMicState('processing');
    setErrorMsg(null);

    try {
      const res = await apiFetch(`/sessions/${sessionId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ text }),
        headers: {
          'Content-Type': 'application/json',
          'X-Idempotency-Key': crypto.randomUUID(),
        },
      });
      setMessages((prev) => [
        ...prev,
        { role: 'user', text: res.transcript, correction: res.correction },
        { role: 'tutor', text: res.tutor_text, audioBase64: res.audio_base64 },
      ]);
      if (res.audio_base64) playBase64Audio(res.audio_base64);
      else setMicState('idle');
    } catch {
      setTextInput(text);
      setErrorMsg('Could not send message. Please press Send to retry.');
      setMicState('idle');
    }
  };

  const handleSlowPlay = async (text: string) => {
    const res = await apiFetch(`/sessions/${sessionId}/slow-tts`, {
      method: 'POST',
      body: JSON.stringify({ text }),
      headers: { 'Content-Type': 'application/json' },
    });
    if (res.audio_base64) playBase64Audio(res.audio_base64);
  };

  const handleHelp = async () => {
    const res = await apiFetch(`/sessions/${sessionId}/help`, { method: 'POST' });
    setSamples(res.samples || []);
  };

  const handleEndSession = async () => {
    await apiFetch(`/sessions/${sessionId}/end`, { method: 'POST' });
    navigate(`/session/${sessionId}/report`);
  };

  return (
    <div className="max-w-2xl mx-auto min-h-screen flex flex-col p-4">
      <header className="flex items-center justify-between py-3 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold">Sam (AI Tutor)</h1>
          <p className="text-sm text-slate-600">Speak slowly and clearly</p>
        </div>
        <button
          onClick={handleEndSession}
          className="flex items-center gap-1 px-4 py-2 rounded-lg bg-rose-100 text-rose-800 font-semibold hover:bg-rose-200"
        >
          <XCircle className="w-5 h-5" /> End Practice
        </button>
      </header>

      {showConsentModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md space-y-4">
            <h2 className="text-xl font-bold">Voice Privacy Notice</h2>
            <p className="text-slate-700 text-base">
              Your voice recording is converted into text in memory and immediately deleted. We only save text transcripts and corrections so you can track your progress.
            </p>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setShowConsentModal(false)} className="px-4 py-2 rounded-lg border border-slate-300">
                Use Text Only
              </button>
              <button
                onClick={() => {
                  localStorage.setItem('Lingo2U_mic_consent', 'true');
                  setHasConsent(true);
                  setShowConsentModal(false);
                }}
                className="px-5 py-2 rounded-lg bg-blue-600 text-white font-semibold"
              >
                I Understand & Allow Mic
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto py-4 space-y-4">
        {messages.map((m, idx) => (
          <div key={idx} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div
              className={`max-w-[85%] rounded-2xl p-4 text-lg ${
                m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border border-slate-200 text-slate-900'
              }`}
            >
              <p>{m.text}</p>
              {m.role === 'tutor' && (
                <div className="flex gap-3 mt-3 pt-2 border-t border-slate-100 text-sm font-medium text-blue-600">
                  <button
                    onClick={() => (m.audioBase64 ? playBase64Audio(m.audioBase64) : handleSlowPlay(m.text))}
                    className="flex items-center gap-1 hover:underline"
                  >
                    <Volume2 className="w-4 h-4" /> Repeat
                  </button>
                  <button onClick={() => handleSlowPlay(m.text)} className="flex items-center gap-1 hover:underline">
                    <Turtle className="w-4 h-4" /> Say it slower
                  </button>
                </div>
              )}
            </div>

            {m.correction && (
              <div className="mt-2 max-w-[85%] bg-amber-50 border border-amber-200 rounded-xl p-3 text-slate-800">
                <p className="text-sm font-semibold text-amber-900">
                  Better way to say it: <span className="underline">{m.correction.corrected}</span>
                </p>
                <p className="text-sm mt-1">{m.correction.reason}</p>
                {m.correction.native_explanation && (
                  <p className="text-xs text-slate-600 mt-1 italic">{m.correction.native_explanation}</p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {samples.length > 0 && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3 mb-3">
          <p className="text-sm font-bold text-emerald-900 mb-1">Try saying one of these:</p>
          <ul className="list-disc list-inside text-base text-emerald-800 space-y-1">
            {samples.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}

      {errorMsg && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 rounded-xl p-3 mb-3 text-sm">{errorMsg}</div>
      )}

      <footer className="pt-3 border-t border-slate-200 space-y-3">
        <div className="flex items-center justify-between gap-4">
          <button
            type="button"
            onClick={handleHelp}
            className="flex items-center gap-2 px-4 py-3 rounded-xl bg-slate-200 text-slate-800 font-semibold"
          >
            <HelpCircle className="w-5 h-5" /> Help me
          </button>

          <button
            type="button"
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onTouchStart={startRecording}
            onTouchEnd={stopRecording}
            disabled={micState === 'processing'}
            className={`flex-1 py-4 rounded-2xl font-bold text-lg flex items-center justify-center gap-2 transition ${
              micState === 'recording'
                ? 'bg-rose-600 text-white animate-pulse'
                : micState === 'processing'
                ? 'bg-slate-400 text-white'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            <Mic className="w-6 h-6" />
            {micState === 'idle' && 'Hold to Speak'}
            {micState === 'recording' && 'Listening... Release to Send'}
            {micState === 'processing' && 'Sam is thinking...'}
            {micState === 'speaking' && 'Sam is speaking...'}
          </button>
        </div>

        <form onSubmit={handleTextSubmit} className="flex gap-2">
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Or type your answer in English..."
            className="flex-1 rounded-xl border border-slate-300 px-4 py-3 text-base"
          />
          <button
            type="submit"
            disabled={micState === 'processing'}
            className="px-5 py-3 rounded-xl bg-slate-800 text-white font-semibold flex items-center gap-1"
          >
            <Send className="w-4 h-4" /> Send
          </button>
        </form>
      </footer>
    </div>
  );
}
