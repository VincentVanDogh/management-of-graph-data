import { Injectable } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {map, Observable} from 'rxjs';
import {PropertyGraphRelation} from "../dtos/property_graph_relation";

@Injectable({
  providedIn: 'root'
})
export class PropertyGraphService {
  // TODO: Add other endpoints / make endpoint dynamic
  private apiUrl = 'http://127.0.0.1:8000';
  private zurichTransportUrl = `${this.apiUrl}/zurich-transport`;
  private cypherUrl = `${this.apiUrl}/cypher`;

  constructor(
    private http: HttpClient
  ) { }

  getTransportData(): Observable<PropertyGraphRelation[]> {
    return this.http.get<{results: PropertyGraphRelation[]}>(this.zurichTransportUrl)
      .pipe(map(x => x.results));
  }

  runCypherQuery(query: string): Observable<any> {
    return this.http.post<any>(this.cypherUrl, { query });
  }
}
