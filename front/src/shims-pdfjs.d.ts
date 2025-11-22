declare module 'pdfjs-dist/build/pdf' {
  export const GlobalWorkerOptions: { workerSrc?: string }
  export const getDocument: (src: any) => { promise: Promise<any> }
}

declare module 'pdfjs-dist/build/pdf.worker.min.mjs?url' {
  const src: string
  export default src
}
