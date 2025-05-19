import { useEffect, useRef } from 'react';
import { useChat } from '../../hooks/useChat';
import Message from './Message';
import InputBox from './InputBox';

export default function ChatWindow() {
  const { messages, sendMessage, loading, error } = useChat();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="container">
      <div className="chat-container">
        <div className="messages">
          {loading && messages.length === 0 ? (
            <div className="loading">Loading chat history...</div>
          ) : error ? (
            <div className="error">{error}</div>
          ) : (
            messages.map((msg, i) => (
              <Message key={i} text={msg.text} isUser={msg.isUser} />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
        <InputBox onSend={sendMessage} disabled={loading} />
      </div>
    </div>
  );
}