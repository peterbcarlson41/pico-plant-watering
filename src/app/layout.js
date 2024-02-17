import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Plant Waterer",
  description: "A web app to control an automatic plant watering system",
  icons: {
    icon: [
      {
        media: "(prefers-color-scheme: light)",
        url: "/plant.png",
        href: "/plant.png",
      },
    ],
  },
};

export default function RootLayout({ children }) {
  return (
    <>
      <html lang="en">
        <body className={inter.className}>{children}</body>
      </html>
    </>
  );
}
