import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { Neo4jPropertyGraphComponent } from './neo4j-property-graph/neo4j-property-graph.component';
import { CustomPropertyGraphComponent } from './custom-property-graph/custom-property-graph.component';

@NgModule({
  declarations: [
    AppComponent,
    Neo4jPropertyGraphComponent,
    CustomPropertyGraphComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
