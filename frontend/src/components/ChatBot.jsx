import { useState } from 'react';
import ChatMessage from './ChatMessage';

function ChatBot({ isOpen, onClose, messages, onSend }) {
  const [draft, setDraft] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!draft.trim()) return;
    onSend(draft.trim());
    setDraft('');
  };

  if (!isOpen) return null;

  return (
    <div className="chat-window">
      <div className="chat-header">
        <h2>AI Shopping Assistant</h2>
        <button type="button" onClick={onClose}>Close</button>
      </div>

      <div className="chat-body">
        {messages.length === 0 ? (
          <p className="empty-state">Ask for a laptop, wallet-friendly headphones, or a product recommendation.</p>
        ) : (
          messages.map((message, index) => (
            <ChatMessage key={`${message.role}-${index}`} message={message} products={message.products || []} />
          ))
        )}
      </div>

      <form className="chat-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="I need a laptop under 70000"
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default ChatBot;
