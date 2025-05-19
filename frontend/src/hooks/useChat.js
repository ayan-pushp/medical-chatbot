import { useState, useEffect } from 'react';
import { chatAPI } from '../services/api';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [dialogState, setDialogState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const data = await chatAPI.getHistory();

        // Map messages, taking care of bot vs user messages
        const formattedMessages = data
          .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp)) // ascending order
          .map(msg => ({
            text: msg.is_user ? msg.message : msg.reply || msg.message || '',
            isUser: msg.is_user
          }));

        setMessages(formattedMessages);

        // Initialize dialogState from the last message in history if available
        // Assuming dialog_state is stored on bot messages (is_user: false)
        const lastBotMsg = [...data].reverse().find(m => !m.is_user && m.dialog_state);
        if (lastBotMsg && lastBotMsg.dialog_state) {
          setDialogState(lastBotMsg.dialog_state);
        } else {
          setDialogState(null);
        }
      } catch (err) {
        console.error('History load error:', err);
        setError('Failed to load history. Please login again.');
      } finally {
        setLoading(false);
      }
    };
    loadHistory();
  }, []);

  const sendMessage = async (message) => {
    const userMsg = { text: message, isUser: true };
    setMessages(prev => [...prev, userMsg]);
  
    try {
      // Transform disease_predictions tuples into dicts
      let dialogStateForSend = dialogState;
      if (dialogStateForSend && dialogStateForSend.disease_predictions) {
        dialogStateForSend = {
          ...dialogStateForSend,
          disease_predictions: dialogStateForSend.disease_predictions.map(dp => ({
            disease: dp[0],
            probability: dp[1],
          })),
        };
      }
  
      const data = await chatAPI.sendMessage(message, dialogStateForSend);
  
      // Keep disease_predictions in tuple format in frontend state for consistency
      if (data.dialog_state?.disease_predictions) {
        data.dialog_state.disease_predictions = data.dialog_state.disease_predictions.map(dp => [dp.disease, dp.probability]);
      }
  
      setMessages(prev => [...prev, {
        text: data.reply,
        isUser: false
      }]);
      setDialogState(data.dialog_state);
    } catch (err) {
      setMessages(prev => [...prev, {
        text: "Sorry, I encountered an error. Please try again.",
        isUser: false
      }]);
      setError('Failed to send message');
      console.error('Send message error:', err);
    }
  };  

  return { messages, sendMessage, loading, error };
}
