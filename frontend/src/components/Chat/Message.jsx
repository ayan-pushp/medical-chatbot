export default function Message({ text, isUser }) {
    if (!text) return null;
  
    return (
      <div className={`message ${isUser ? 'user' : 'bot'}`}>
        {text.split('\n').map((line, i) => (
          <p key={i}>{line}</p>
        ))}
      </div>
    );
  }
  