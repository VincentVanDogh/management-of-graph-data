import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {CustomPropertyGraphComponent} from "./custom-property-graph/custom-property-graph.component";
import {RdfComponent} from "./rdf/rdf/rdf.component";

const routes: Routes = [
  {path: '', component: CustomPropertyGraphComponent},
  {path: 'rdf', component: RdfComponent},
  {path: 'lpg', component: CustomPropertyGraphComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
