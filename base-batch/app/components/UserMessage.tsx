import { CiUser } from "react-icons/ci";
import { motion } from "framer-motion";

interface UserMessageProps {
  newMessage: string;
}

const UserMessage = ({ newMessage }: UserMessageProps) => {
  const date = new Date();
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex w-full my-3 items-start justify-end gap-3"
    >
      <motion.div
        initial={{ scale: 0.95 }}
        animate={{ scale: 1 }}
        className="inline-block rounded-2xl bg-gradient-to-br from-indigo-500 to-indigo-600 p-4 text-lg text-white max-w-[75%] break-words shadow-md hover:shadow-lg transition-shadow"
      >
        {newMessage}
        <div className="text-right mt-2">
          <span className="text-xs text-white/80">
            {date.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
        </div>
      </motion.div>

      <div className="flex justify-center items-center w-10 h-10 border-2 border-indigo-400 bg-slate-800 rounded-full shadow-lg">
        <CiUser size={24} className="text-indigo-400" />
      </div>
    </motion.div>
  );
};

export default UserMessage;
