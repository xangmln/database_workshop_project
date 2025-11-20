export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-900 text-white">
      <h1 className="text-4xl font-bold mb-4">main home page</h1>
      <p className="text-lg text-slate-300">
        Tailwind 유틸 잘 들어오면 이 텍스트도 꾸며져 보일 거야.
      </p>
      <button className="mt-6 px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600">
        Login으로 가기
      </button>
    </div>
  );
}
