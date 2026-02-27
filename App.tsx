import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Overview from './screens/Overview';
import Settings from './screens/Settings';
import ReviewQueue from './screens/ReviewQueue';
import TikTokHub from './screens/TikTokHub';
import InstagramHub from './screens/InstagramHub';
import XHub from './screens/XHub';
import AIPersonality from './screens/AIPersonality';
import CommentLibrary from './screens/CommentLibrary';
import AILearning from './screens/AILearning';

export type RoutePath = '/overview' | '/review' | '/settings' | '/hub/tiktok' | '/hub/instagram' | '/hub/x' | '/personas' | '/library' | '/learning';

export default function App() {
  const [currentRoute, setCurrentRoute] = useState<RoutePath>('/overview');

  const renderScreen = () => {
    switch (currentRoute) {
      case '/overview':
        return <Overview onNavigate={setCurrentRoute} />;
      case '/review':
        return <ReviewQueue />;
      case '/settings':
        return <Settings />;
      case '/hub/tiktok':
        return <TikTokHub />;
      case '/hub/instagram':
        return <InstagramHub />;
      case '/hub/x':
        return <XHub />;
      case '/personas':
        return <AIPersonality />;
      case '/library':
        return <CommentLibrary />;
      case '/learning':
        return <AILearning />;
      default:
        return <Overview onNavigate={setCurrentRoute} />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#0B0F1A] text-white">
      <Sidebar currentRoute={currentRoute} onNavigate={setCurrentRoute} />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {renderScreen()}
      </div>
    </div>
  );
}