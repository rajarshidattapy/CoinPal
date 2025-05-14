const TypingIndicator = () => {
  return (
    <div className="flex items-start my-3 gap-3">
      <div className="flex justify-center items-center w-10 h-10 border-2 border-blue-400 bg-slate-800 rounded-full shadow-lg">
        <div className="flex items-center justify-center w-6 h-3">
          <div className="w-1.5 h-1.5 mx-0.5 bg-blue-400 rounded-full animate-bounce [animation-delay:0s]"></div>
          <div className="w-1.5 h-1.5 mx-0.5 bg-blue-400 rounded-full animate-bounce [animation-delay:0.15s]"></div>
          <div className="w-1.5 h-1.5 mx-0.5 bg-blue-400 rounded-full animate-bounce [animation-delay:0.3s]"></div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
