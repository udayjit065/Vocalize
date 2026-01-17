import type { NextConfig } from "next";

const nextConfig: any = {
  devIndicators: false,
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
