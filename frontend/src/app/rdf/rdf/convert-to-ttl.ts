// convert-to-ttl.ts
export function convertToTTL(products: any[]): string {
  let ttl = `
@prefix ex: <http://localhost/openaire/rp/> .
@prefix schema: <http://schema.org/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
`;

  products.forEach(p => {
    ttl += `
ex:${p.id}
    a schema:CreativeWork ;
    schema:identifier "${p.identifier}" ;
    schema:name "${p.name}" ;
    schema:alternateName "${p.alternateName || ''}" ;
    dcterms:accessRights "${p.accessRights || ''}" ;
    dcterms:publisher "${p.publisher || ''}" ;
    dcterms:issued "${p.issued || ''}"^^xsd:date ;
    dcterms:subject "${(p.subjects || []).join('" , "')}" ;
    dcterms:language "${p.language || ''}" .
`;
  });

  return ttl;
}