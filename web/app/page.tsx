import { TmaInit } from "./components/TmaInit";

export const dynamic = "force-dynamic";

type Product = {
  id: number;
  name: string;
  image_url: string;
  created_at: string;
};

function resolveApiBase(): string {
  if (process.env.INTERNAL_API_URL) {
    return process.env.INTERNAL_API_URL;
  }
  const host = process.env.API_INTERNAL_HOST;
  const port = process.env.API_INTERNAL_PORT;
  if (host && port) {
    return `http://${host}:${port}`;
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

async function fetchProducts(): Promise<Product[]> {
  const base = resolveApiBase();
  const res = await fetch(`${base}/api/products`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API responded with ${res.status}`);
  }
  return res.json();
}

export default async function CatalogPage() {
  let products: Product[] = [];
  let error: string | null = null;

  try {
    products = await fetchProducts();
  } catch (e) {
    error = e instanceof Error ? e.message : "Не удалось загрузить каталог";
  }

  return (
    <main>
      <TmaInit />
      <h1>Каталог</h1>
      {error && <p className="error">{error}</p>}
      {!error && products.length === 0 && (
        <p className="empty">Пока нет товаров.</p>
      )}
      {!error && products.length > 0 && (
        <ul>
          {products.map((p) => (
            <li key={p.id}>
              <strong>{p.name}</strong>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={p.image_url} alt={p.name} loading="lazy" />
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
