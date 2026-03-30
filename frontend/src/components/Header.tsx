"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Header() {
  const pathname = usePathname();

  const linkClass = (path: string) =>
    `px-4 py-2 rounded-md text-sm font-medium transition-colors ${
      pathname === path
        ? "bg-blue-600 text-white"
        : "text-gray-600 hover:bg-gray-200"
    }`;

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-gray-800">
          RAG Knowledge Hub
        </Link>
        <nav className="flex gap-2">
          <Link href="/chat" className={linkClass("/chat")}>
            質問する
          </Link>
          <Link href="/admin" className={linkClass("/admin")}>
            文書管理
          </Link>
        </nav>
      </div>
    </header>
  );
}
