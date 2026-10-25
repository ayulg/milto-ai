import { Link } from 'react-router-dom';
import { ArrowRightIcon, SparklesIcon, AcademicCapIcon, ChartBarIcon } from '@heroicons/react/24/outline';

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <header className="border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary-900 flex items-center justify-center font-bold text-xl">
              M
            </div>
            <span className="font-display font-bold text-2xl">Milto AI</span>
          </div>
          <nav className="flex gap-3">
            <Link to="/login" className="btn btn-secondary text-sm">Sign In</Link>
            <Link to="/assessment" className="btn btn-primary text-sm">Start Assessment</Link>
          </nav>
        </div>
      </header>

      <section className="max-w-7xl mx-auto px-6 py-20 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm mb-8">
          <SparklesIcon className="w-4 h-4 text-[#d2a277]" />
          <span>AI-Powered Career Guidance for Ethiopian Universities</span>
        </div>

        <h1 className="font-display font-extrabold text-5xl md:text-7xl mb-6 leading-tight">
          Find your direction.
          <br />
          <span className="text-[#d2a277]">Test it in real life.</span>
        </h1>

        <p className="text-lg md:text-xl text-gray-400 max-w-3xl mx-auto mb-10">
          Milto combines personality, interests, skills, and real-world feedback to help you explore careers without reducing you to one test result.
        </p>

        <div className="flex flex-wrap gap-4 justify-center">
          <Link to="/assessment" className="btn btn-primary text-base px-8 py-4">
            Start Your Assessment
            <ArrowRightIcon className="w-5 h-5" />
          </Link>
          <Link to="/career-lab" className="btn btn-secondary text-base px-8 py-4">
            Explore Careers
          </Link>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-6 py-16">
        <div className="grid md:grid-cols-3 gap-6">
          <FeatureCard
            icon={<AcademicCapIcon className="w-8 h-8" />}
            title="10-Level Analysis"
            description="Comprehensive personality assessment with detailed match percentages for 10 careers."
          />
          <FeatureCard
            icon={<ChartBarIcon className="w-8 h-8" />}
            title="Career Match Rates"
            description="See exactly how well each career matches your unique personality profile."
          />
          <FeatureCard
            icon={<SparklesIcon className="w-8 h-8" />}
            title="AI Coach"
            description="Personalized career guidance for Ethiopian universities and job market."
          />
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-6 py-16 text-center">
        <div className="glass-card p-8 inline-block">
          <div className="flex items-center gap-3 justify-center">
            <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-sm text-gray-400">
              
            </span>
          </div>
        </div>
      </section>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="glass-card p-6 hover:border-[#d2a277]/30 transition-all">
      <div className="w-14 h-14 rounded-2xl bg-[#d2a277]/10 flex items-center justify-center mb-4 text-[#d2a277]">
        {icon}
      </div>
      <h3 className="font-display font-bold text-xl mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  );
}

