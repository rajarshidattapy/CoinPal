"use client";
import { useState } from "react";
import axios from "axios";
import BotMessage from "./BotMessage";
import TypingIndicator from "./TypingIndicator";
import UserMessage from "./UserMessage";

const ChatBot = () => {
  const [newMessage, setNewMessage] = useState<string>("");
  const [messages, setMessages] = useState<{ from: string; text: string }[]>(
    []
  );
  const [showChat, setShowChat] = useState<boolean>(true);
  const [isTyping, setIsTyping] = useState(false);

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;
    const userMsg = { from: "user", text: newMessage };
    setMessages((prev) => [...prev, userMsg]);
    setNewMessage("");
    setIsTyping(true);
    try {
      const res = await axios.post(
        "http://127.0.0.1:3001/api/chat",
        {
          message: newMessage,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      const botMsg = { from: "bot", text: res.data };
      setMessages((prev) => [...prev, botMsg]);
      console.log(messages);
      setNewMessage("");
    } catch (err) {
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };
  return (
    <>
      {showChat && (
        <div className="flex justify-center items-center h-full w-full">
          <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 h-[600px] w-1/2 overflow-hidden">
            <div className="flex flex-col h-full">
              <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-blue-500 scrollbar-track-gray-100">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full space-y-4">
                    <span className="text-6xl">💰</span>
                    <p className="text-gray-800 text-center text-lg font-medium">
                      Welcome to CoinPal!
                    </p>
                    <p className="text-gray-500 text-sm text-center max-w-sm">
                      Ask me about cryptocurrency prices, market trends, or
                      investment advice!
                    </p>
                  </div>
                ) : (
                  <>
                    {messages.map((msg: any, index: number) =>
                      msg.from === "user" ? (
                        <UserMessage key={index} newMessage={msg.text} />
                      ) : (
                        <BotMessage key={index} botMessage={msg.text} />
                      )
                    )}
                    {isTyping && <TypingIndicator />}
                  </>
                )}
              </div>

              <div className="p-4 border-t border-gray-200 bg-white rounded-b-2xl">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="flex flex-row space-x-2"
                >
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    className="flex-1 py-2.5 px-4 bg-gray-50 text-gray-900 rounded-lg border border-gray-200 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 placeholder-gray-400 transition-all duration-200"
                    placeholder="Ask about crypto..."
                  />
                  <button
                    type="submit"
                    disabled={!newMessage.trim()}
                    className="py-2.5 px-6 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-500 flex items-center gap-2"
                  >
                    Send
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatBot;
