import React, { useState, useEffect } from 'react';
import { Clock, TrendingUp, Target } from 'lucide-react';
import axios from 'axios';

interface ProgressIndicatorProps {
  className?: string;
  isVisible?: boolean;
  onToggle?: () => void;
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({ 
  className = "", 
  isVisible = true, 
  onToggle 
}) => {
  const [sessionTime, setSessionTime] = useState(0);
  const [topicsCount, setTopicsCount] = useState(0);
  const [currentTopic, setCurrentTopic] = useState("");
  const [recentResult, setRecentResult] = useState<{ type: 'correct' | 'incorrect', timestamp: number } | null>(null);

  useEffect(() => {
    if (!isVisible) return;

    // Update session time every minute
    const timeInterval = setInterval(() => {
      setSessionTime(prev => prev + 1);
    }, 60000);

    // Fetch progress every 30 seconds
    const progressInterval = setInterval(fetchQuickProgress, 30000);

    // Initial fetch
    fetchQuickProgress();

    return () => {
      clearInterval(timeInterval);
      clearInterval(progressInterval);
    };
  }, [isVisible]);

  const fetchQuickProgress = async () => {
    try {
      const response = await axios.get('http://localhost:8000/learning/progress');
      const progress = response.data;
      
      setSessionTime(progress.session_duration || 0);
      setTopicsCount(progress.completed_topics || 0);
      setCurrentTopic(progress.last_topic || "");
    } catch (err) {
      console.error('Error fetching quick progress:', err);
    }
  };

  // Listen for answer validation events to refresh progress immediately
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'answerValidated') {
        fetchQuickProgress();
      }
    };

    const handleAnswerResult = (e: StorageEvent) => {
      if (e.key === 'answerResult') {
        const result = JSON.parse(e.newValue || '{}');
        setRecentResult({
          type: result.isCorrect ? 'correct' : 'incorrect',
          timestamp: Date.now()
        });
        
        // Clear the result after 3 seconds
        setTimeout(() => {
          setRecentResult(null);
        }, 3000);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('storage', handleAnswerResult);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('storage', handleAnswerResult);
    };
  }, []);

  const formatTime = (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes}m`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  if (!isVisible && onToggle) {
    return (
      <button
        onClick={onToggle}
        className={`bg-blue-600 text-white p-2 rounded-full shadow-lg hover:bg-blue-700 transition-colors ${className}`}
        title="Show Progress"
      >
        <TrendingUp className="w-4 h-4" />
      </button>
    );
  }

  if (!isVisible) return null;

  return (
    <div className={`bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-3 border border-gray-200 relative ${className}`}>
      {/* Recent Result Indicator */}
      {recentResult && (
        <div className={`absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold animate-pulse
          ${recentResult.type === 'correct' ? 'bg-green-500' : 'bg-red-500'}`}>
          {recentResult.type === 'correct' ? '✓' : '✗'}
        </div>
      )}
      
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4 text-sm">
          {/* Session Time */}
          <div className="flex items-center space-x-1">
            <Clock className="w-4 h-4 text-blue-600" />
            <span className="text-gray-700">{formatTime(sessionTime)}</span>
          </div>

          {/* Topics Count */}
          <div className="flex items-center space-x-1">
            <Target className="w-4 h-4 text-green-600" />
            <span className="text-gray-700">{topicsCount} topics</span>
          </div>

          {/* Current Topic */}
          {currentTopic && (
            <div className="flex items-center space-x-1">
              <TrendingUp className="w-4 h-4 text-purple-600" />
              <span className="text-gray-700 truncate max-w-24" title={currentTopic}>
                {currentTopic}
              </span>
            </div>
          )}
        </div>

        {/* Hide Button */}
        {onToggle && (
          <button
            onClick={onToggle}
            className="ml-2 text-gray-400 hover:text-gray-600 p-1"
            title="Hide Progress"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
};

export default ProgressIndicator;