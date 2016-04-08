/***************************************************************************
 *   Copyright (c) 2013 Jan Rheinländer <jrheinlaender@users.sourceforge.net>        *
 *                                                                         *
 *   This file is part of the FreeCAD CAx development system.              *
 *                                                                         *
 *   This library is free software; you can redistribute it and/or         *
 *   modify it under the terms of the GNU Library General Public           *
 *   License as published by the Free Software Foundation; either          *
 *   version 2 of the License, or (at your option) any later version.      *
 *                                                                         *
 *   This library  is distributed in the hope that it will be useful,      *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU Library General Public License for more details.                  *
 *                                                                         *
 *   You should have received a copy of the GNU Library General Public     *
 *   License along with this library; see the file COPYING.LIB. If not,    *
 *   write to the Free Software Foundation, Inc., 59 Temple Place,         *
 *   Suite 330, Boston, MA  02111-1307, USA                                *
 *                                                                         *
 ***************************************************************************/


#include "PreCompiled.h"

#ifndef _PreComp_
# include <sstream>
# include <QRegExp>
# include <QTextStream>
# include <QMessageBox>
# include <Precision.hxx>
# include <TopoDS.hxx>
# include <BRepAdaptor_Surface.hxx>
# include <Geom_Plane.hxx>
# include <gp_Pln.hxx>
# include <gp_Ax1.hxx>
# include <BRepAdaptor_Curve.hxx>
# include <Geom_Line.hxx>
# include <gp_Lin.hxx>
#endif

#include "ui_TaskFemFluidBoundary.h"
#include "TaskFemFluidBoundary.h"
#include <App/Application.h>
#include <App/Document.h>
#include <App/PropertyGeo.h>
#include <Gui/Application.h>
#include <Gui/Document.h>
#include <Gui/BitmapFactory.h>
#include <Gui/ViewProvider.h>
#include <Gui/WaitCursor.h>
#include <Gui/Selection.h>
#include <Gui/Command.h>
#include <Mod/Fem/App/FemFluidBoundary.h>
#include <Mod/Fem/App/FemTools.h>
#include <Mod/Part/App/PartFeature.h>

#include <Base/Console.h>
#include <Base/Tools.h>

using namespace FemGui;
using namespace Gui;

/* TRANSLATOR FemGui::TaskFemFluidBoundary */

TaskFemFluidBoundary::TaskFemFluidBoundary(ViewProviderFemFluidBoundary *ConstraintView,QWidget *parent)
    : TaskFemConstraint(ConstraintView, parent, "fem-fluid-boundary")
{
    // we need a separate container widget to add all controls to
    proxy = new QWidget(this);
    ui = new Ui_TaskFemFluidBoundary();
    ui->setupUi(proxy);
    QMetaObject::connectSlotsByName(this);

    // Create a context menu for the listview of the references
    QAction* action = new QAction(tr("Delete"), ui->listReferences);
    action->connect(action, SIGNAL(triggered()),
                    this, SLOT(onReferenceDeleted()));
    ui->listReferences->addAction(action);
    ui->listReferences->setContextMenuPolicy(Qt::ActionsContextMenu);

    connect(ui->comboBoundaryType, SIGNAL(currentIndexChanged(int)),
            this, SLOT(onBoundaryTypeChanged(void)));
    connect(ui->comboSubtype, SIGNAL(currentIndexChanged(int)),
            this, SLOT(onSubtypeChanged(void)));
    connect(ui->spinBoundaryValue, SIGNAL(valueChanged(double)),
            this, SLOT(onBoundaryValueChanged(double)));
    connect(ui->buttonReference, SIGNAL(pressed()),
            this, SLOT(onButtonReference()));
    connect(ui->buttonDirection, SIGNAL(pressed()),
            this, SLOT(onButtonDirection()));
    connect(ui->checkReverse, SIGNAL(toggled(bool)),
            this, SLOT(onCheckReverse(bool)));

    this->groupLayout()->addWidget(proxy);

    // Temporarily prevent unnecessary feature recomputes
    ui->spinBoundaryValue->blockSignals(true);
    ui->listReferences->blockSignals(true);
    
    ui->buttonReference->blockSignals(true);
    ui->buttonDirection->blockSignals(true);
    ui->checkReverse->blockSignals(true);

    // Get the feature data
    Fem::FluidBoundary* pcConstraint = static_cast<Fem::FluidBoundary*>(ConstraintView->getObject());
    double f = pcConstraint->BoundaryValue.getValue();
    Base::Console().Message("just before updateBoundaryTypeUI\n");
    
    ui->comboBoundaryType->blockSignals(true);
    std::vector<std::string> boundaryTypes = pcConstraint->BoundaryType.getEnumVector();
    ui->comboBoundaryType->clear();
    for (int it = 0; it < boundaryTypes.size(); it++)
    {
        //Base::Console().Message(boundaryTypes[it].c_str());
        ui->comboBoundaryType->insertItem(it, Base::Tools::fromStdString(boundaryTypes[it]));
    }
    ui->comboBoundaryType->blockSignals(false);
    ui->comboBoundaryType->setCurrentIndex(pcConstraint->BoundaryType.getValue());
    
    updateBoundaryTypeUI();
    updateSubtypeUI();
    //* Base::Console().Message("just after updateBoundaryTypeUI\n");
    
    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();
    std::vector<std::string> dirStrings = pcConstraint->Direction.getSubValues();
    QString dir;
    if (!dirStrings.empty())
        dir = makeRefText(pcConstraint->Direction.getValue(), dirStrings.front());
    bool reversed = pcConstraint->Reversed.getValue();

    // Fill data into dialog elements
    ui->spinBoundaryValue->setMinimum(0);
    ui->spinBoundaryValue->setMaximum(FLOAT_MAX);
    ui->spinBoundaryValue->setValue(f);
    ui->listReferences->clear();
    for (std::size_t i = 0; i < Objects.size(); i++)
        ui->listReferences->addItem(makeRefText(Objects[i], SubElements[i]));
    if (Objects.size() > 0)
        ui->listReferences->setCurrentRow(0, QItemSelectionModel::ClearAndSelect);
    ui->lineDirection->setText(dir.isEmpty() ? tr("") : dir);
    //ui->checkReverse->setChecked(reversed);
    ui->checkReverse->setVisible(false); // no need such UI for fluid boundary

    ui->listReferences->blockSignals(false);
    ui->buttonReference->blockSignals(false);

    ui->spinBoundaryValue->blockSignals(false);
    ui->buttonDirection->blockSignals(false);
    ui->checkReverse->blockSignals(false);

    updateSelectionUI();
}

const char* WallSubtypes[] = {"unspecific", "fixed",NULL};
const char* InletSubtypes[] = {"totalPressure","uniformVelocity","flowrate","userDefined",NULL};
const char* OutletSubtypes[] = {"totalPressure","uniformVelocity","flowrate","userDefined",NULL};
const char* InterfaceSubtypes[] = {"symmetry","wedge","cyclic","empty", NULL};
const char* FreestreamSubtypes[] = {"freestream",NULL};

void TaskFemFluidBoundary::updateBoundaryTypeUI()
{
        
    Fem::FluidBoundary* pcConstraint = static_cast<Fem::FluidBoundary*>(ConstraintView->getObject());
    std::string boundaryType = pcConstraint->BoundaryType.getValueAsString();
    
    // Update subtypes, any change here should be written back to FemFluidBoundary.cpp
    if (boundaryType == "wall") 
    {
        ui->frameBoundaryValue->setVisible(false);

        pcConstraint->Subtype.setEnums(WallSubtypes);
    }
    else if (boundaryType == "interface")
    {
        ui->frameBoundaryValue->setVisible(false);
        pcConstraint->Subtype.setEnums(InterfaceSubtypes);
    }
    else if (boundaryType == "freestream")
    {
        ui->frameBoundaryValue->setVisible(false);

        pcConstraint->Subtype.setEnums(FreestreamSubtypes);
    }
    else if(boundaryType == "inlet")
    {
        ui->frameBoundaryValue->setVisible(true);
        ui->labelSubtype->setText(QString::fromUtf8("valueType"));
        pcConstraint->Subtype.setEnums(InletSubtypes);
        pcConstraint->Reversed.setValue(true); // inlet must point into volume
    }
    else if(boundaryType == "outlet")
    {
        ui->frameBoundaryValue->setVisible(true);
        ui->labelSubtype->setText(QString::fromUtf8("valueType"));
        pcConstraint->Subtype.setEnums(OutletSubtypes);
        pcConstraint->Reversed.setValue(false); // inlet must point outside
    }
    else
    {
        Base::Console().Message(boundaryType.c_str());
        Base::Console().Message("Error boundaryType is not defined\n");
    }
    
    Base::Console().Message("\n before set comboSubtype items\n");
    ui->comboSubtype->blockSignals(true);
    std::vector<std::string> subtypes = pcConstraint->Subtype.getEnumVector();
    std::string sSubtype = pcConstraint->Subtype.getValueAsString();
    int iSubtype = 0;
    ui->comboSubtype->clear();
    for (int it = 0; it < subtypes.size(); it++)
    {
        ui->comboSubtype->insertItem(it, Base::Tools::fromStdString(subtypes[it]));
        if (sSubtype == subtypes[it])
        {
            iSubtype = it;
        }
    }
    ui->comboSubtype->blockSignals(false);
    ui->comboSubtype->setCurrentIndex(iSubtype);

}

void TaskFemFluidBoundary::updateSubtypeUI()
{

    Fem::FluidBoundary* pcConstraint = static_cast<Fem::FluidBoundary*>(ConstraintView->getObject());
    //* Subtype PropertyEnumeration is updated if BoundaryType is changed
    std::string boundaryType = pcConstraint->BoundaryType.getValueAsString(); 
    
    if(boundaryType == "inlet" || boundaryType == "outlet")
    {
        std::string subtype = Base::Tools::toStdString(ui->comboSubtype->currentText()); 
        
        Base::Console().Message("\nsubtype property:");
        Base::Console().Message(subtype.c_str());
        if (subtype == "totalPressure")
        {
            ui->labelBoundaryValue->setText(QString::fromUtf8("pressure [Pa]")); //* tr()
        }
        else if (subtype == "uniformVelocity")
        {
            ui->labelBoundaryValue->setText(QString::fromUtf8("velocity [m/s]"));
        }
        else if (subtype == "flowrate")
        {
            ui->labelBoundaryValue->setText(QString::fromUtf8("flowrate [kg/s]"));
        }
        else
        {
            ui->labelBoundaryValue->setText(QString::fromUtf8("userDefined"));
        }
    }
    
}

void TaskFemFluidBoundary::updateSelectionUI()
{
    if (ui->listReferences->model()->rowCount() == 0) {
        // Go into reference selection mode if no reference has been selected yet
        onButtonReference(true);
        return;
    }
    
    /** not needed for fluid boundary, as it must be Face
    std::string ref = ui->listReferences->item(0)->text().toStdString();
    int pos = ref.find_last_of(":");
    if (ref.substr(pos+1, 6) == "Vertex")
        ui->labelForce->setText(tr("Point load"));
    else if (ref.substr(pos+1, 4) == "Edge")
        ui->labelForce->setText(tr("Line load"));
    else if (ref.substr(pos+1, 4) == "Face")
        ui->labelForce->setText(tr("Area load"));
    */
}

void TaskFemFluidBoundary::onSelectionChanged(const Gui::SelectionChanges& msg)
{
    if (msg.Type == Gui::SelectionChanges::AddSelection) {
        // Don't allow selection in other document
        if (strcmp(msg.pDocName, ConstraintView->getObject()->getDocument()->getName()) != 0)
            return;

        if (!msg.pSubName || msg.pSubName[0] == '\0')
            return;
        std::string subName(msg.pSubName);

        if (selectionMode == selnone)
            return;

        std::vector<std::string> references(1,subName);
        Fem::FluidBoundary* pcConstraint = static_cast<Fem::FluidBoundary*>(ConstraintView->getObject());
        App::DocumentObject* obj = ConstraintView->getObject()->getDocument()->getObject(msg.pObjectName);
        Part::Feature* feat = static_cast<Part::Feature*>(obj);
        TopoDS_Shape ref = feat->Shape.getShape().getSubShape(subName.c_str());
        //* string conversion:  <Base/Tools.h> toStdString()/fromStdString()
        if (selectionMode == selref) {
            std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
            std::vector<std::string> SubElements = pcConstraint->References.getSubValues();

            // Ensure we don't have mixed reference types
            if (SubElements.size() > 0) {
                if (subName.substr(0,4) != SubElements.front().substr(0,4)) {
                    QMessageBox::warning(this, tr("Selection error"), tr("Mixed shape types are not possible. Use a second constraint instead"));
                    return;
                }
            }
            else {
                if ((subName.substr(0,4) != "Face") && (subName.substr(0,4) != "Edge") && (subName.substr(0,6) != "Vertex")) {
                    QMessageBox::warning(this, tr("Selection error"), tr("Only faces, edges and vertices can be picked"));
                    return;
                }
            }

            // Avoid duplicates
            std::size_t pos = 0;
            for (; pos < Objects.size(); pos++) {
                if (obj == Objects[pos]) {
                    break;
                }
            }

            if (pos != Objects.size()) {
                if (subName == SubElements[pos]) {
                    return;
                }
            }

            // add the new reference
            Objects.push_back(obj);
            SubElements.push_back(subName);
            pcConstraint->References.setValues(Objects,SubElements);
            ui->listReferences->addItem(makeRefText(obj, subName));

            // Turn off reference selection mode
            onButtonReference(false);
        }
        else if (selectionMode == seldir) {
            if (subName.substr(0,4) == "Face") {
                if (!Fem::Tools::isPlanar(TopoDS::Face(ref))) {
                    QMessageBox::warning(this, tr("Selection error"), tr("Only planar faces can be picked"));
                    return;
                }
            }
            else if (subName.substr(0,4) == "Edge") {
                if (!Fem::Tools::isLinear(TopoDS::Edge(ref))) {
                    QMessageBox::warning(this, tr("Selection error"), tr("Only linear edges can be picked"));
                    return;
                }
            }
            else {
                QMessageBox::warning(this, tr("Selection error"), tr("Only faces and edges can be picked"));
                return;
            }
            pcConstraint->Direction.setValue(obj, references);
            ui->lineDirection->setText(makeRefText(obj, subName));

            // Turn off direction selection mode
            onButtonDirection(false);
        }

        Gui::Selection().clearSelection();
        updateSelectionUI();
    }
}

void TaskFemFluidBoundary::onBoundaryTypeChanged(void)
{
    Fem::FluidBoundary* pcConstraint = static_cast<Fem::FluidBoundary*>(ConstraintView->getObject());
    pcConstraint->BoundaryType.setValue(ui->comboBoundaryType->currentIndex());   
    updateBoundaryTypeUI();
}

void TaskFemFluidBoundary::onSubtypeChanged(void)
{
    Fem::FluidBoundary* pcConstraint = static_cast<Fem::FluidBoundary*>(ConstraintView->getObject());
    pcConstraint->Subtype.setValue(ui->comboSubtype->currentIndex());
    updateSubtypeUI();
}

void TaskFemFluidBoundary::onBoundaryValueChanged(double f)
{
    Fem::FluidBoundary* pcConstraint = static_cast<Fem::FluidBoundary*>(ConstraintView->getObject());
    pcConstraint->BoundaryValue.setValue(f);
}

void TaskFemFluidBoundary::onReferenceDeleted() {
    int row = ui->listReferences->currentIndex().row();
    TaskFemConstraint::onReferenceDeleted(row);
    ui->listReferences->model()->removeRow(row);
    ui->listReferences->setCurrentRow(0, QItemSelectionModel::ClearAndSelect);
}

void TaskFemFluidBoundary::onButtonDirection(const bool pressed) {
    if (pressed) {
        selectionMode = seldir;
    } else {
        selectionMode = selnone;
    }
    ui->buttonDirection->setChecked(pressed);
    Gui::Selection().clearSelection();
}

void TaskFemFluidBoundary::onCheckReverse(const bool pressed)
{
    Fem::FluidBoundary* pcConstraint = static_cast<Fem::FluidBoundary*>(ConstraintView->getObject());
    pcConstraint->Reversed.setValue(pressed);
}

std::string TaskFemFluidBoundary::getBoundaryType(void) const
{
    return Base::Tools::toStdString(ui->comboBoundaryType->currentText());
}

std::string TaskFemFluidBoundary::getSubtype(void) const
{
    return Base::Tools::toStdString(ui->comboSubtype->currentText());
}

double TaskFemFluidBoundary::getBoundaryValue(void) const
{
    return ui->spinBoundaryValue->value();
}

const std::string TaskFemFluidBoundary::getReferences() const
{
    int rows = ui->listReferences->model()->rowCount();

    std::vector<std::string> items;
    for (int r = 0; r < rows; r++)
        items.push_back(ui->listReferences->item(r)->text().toStdString());
    return TaskFemConstraint::getReferences(items);
}

const std::string TaskFemFluidBoundary::getDirectionName(void) const
{
    std::string dir = ui->lineDirection->text().toStdString();
    if (dir.empty())
        return "";

    int pos = dir.find_last_of(":");
    return dir.substr(0, pos).c_str();
}

const std::string TaskFemFluidBoundary::getDirectionObject(void) const
{
    std::string dir = ui->lineDirection->text().toStdString();
    if (dir.empty())
        return "";

    int pos = dir.find_last_of(":");
    return dir.substr(pos+1).c_str();
}

bool TaskFemFluidBoundary::getReverse() const
{
    return ui->checkReverse->isChecked();
}

TaskFemFluidBoundary::~TaskFemFluidBoundary()
{
    delete ui;
}

void TaskFemFluidBoundary::changeEvent(QEvent *e)
{
    TaskBox::changeEvent(e);
    if (e->type() == QEvent::LanguageChange) {
        ui->spinBoundaryValue->blockSignals(true);
        //more ui widget? those UI are does not support tr yet!
        ui->retranslateUi(proxy);
        
        ui->spinBoundaryValue->blockSignals(false);
    }
}

//**************************************************************************
//**************************************************************************
// TaskDialog
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TaskDlgFemFluidBoundary::TaskDlgFemFluidBoundary(ViewProviderFemFluidBoundary *ConstraintView)
{
    this->ConstraintView = ConstraintView;
    assert(ConstraintView);
    this->parameter = new TaskFemFluidBoundary(ConstraintView);;

    Content.push_back(parameter);
}

//==== calls from the TaskView ===============================================================

void TaskDlgFemFluidBoundary::open()
{
    // a transaction is already open at creation time of the panel
    if (!Gui::Command::hasPendingCommand()) {
        QString msg = QObject::tr("Constraint force");
        Gui::Command::openCommand((const char*)msg.toUtf8());
    }
}

bool TaskDlgFemFluidBoundary::accept()
{
    std::string name = ConstraintView->getObject()->getNameInDocument();
    const TaskFemFluidBoundary* boundary = static_cast<const TaskFemFluidBoundary*>(parameter);

    try {
        //Gui::Command::openCommand("Fluid boundary condition changed");
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.BoundaryType = '%s'",name.c_str(), boundary->getBoundaryType().c_str());
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Subtype = '%s'",name.c_str(), boundary->getSubtype().c_str());
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.BoundaryValue = %f",name.c_str(), boundary->getBoundaryValue());
        
        std::string dirname = boundary->getDirectionName().data();
        std::string dirobj = boundary->getDirectionObject().data();

        if (!dirname.empty()) {
            QString buf = QString::fromUtf8("(App.ActiveDocument.%1,[\"%2\"])");
            buf = buf.arg(QString::fromStdString(dirname));
            buf = buf.arg(QString::fromStdString(dirobj));
            Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Direction = %s", name.c_str(), buf.toStdString().c_str());
        } else {
            Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Direction = None", name.c_str());
        }
        //Reverse controll is done at BoundaryType selection, this UI is hiden from user
        //Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Reversed = %s", name.c_str(), boundary->getReverse() ? "True" : "False");
    }
    catch (const Base::Exception& e) {
        QMessageBox::warning(parameter, tr("Input error"), QString::fromLatin1(e.what()));
        return false;
    }

    return TaskDlgFemConstraint::accept();
}

bool TaskDlgFemFluidBoundary::reject()
{
    // roll back the changes
    Gui::Command::abortCommand();
    Gui::Command::doCommand(Gui::Command::Gui,"Gui.activeDocument().resetEdit()");
    Gui::Command::updateActive();

    return true;
}

#include "moc_TaskFemFluidBoundary.cpp"
